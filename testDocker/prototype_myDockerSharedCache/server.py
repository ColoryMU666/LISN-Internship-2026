from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
import shutil
import os
import subprocess
import shlex
import re
import tempfile
import tomllib
from urllib.parse import urlparse
from typing import Optional

PLATFORM_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
VERSION_RE  = re.compile(r'^\d+\.\d+(\.\d+)?$')
MAX_LOCKFILE_SIZE = 1 * 1024 * 1024  # 1 MB
ALLOWED_HOST = "files.pythonhosted.org"

app = FastAPI()

def validate_lockfile(content: bytes) -> None:
    try:
        data = tomllib.loads(content.decode("utf-8"))
    except tomllib.TOMLDecodeError:
        raise HTTPException(status_code=400, detail="Invalid TOML format")

    if "packages" not in data:
        raise HTTPException(status_code=400, detail="Not a valid pylock.toml: missing 'packages' section")
    
    for package in data["packages"]:
        name = package.get("name", "<unknown>")

        if "vcs" in package:
            raise HTTPException(status_code=400, detail=f"VCS dependencies are not allowed (package '{name}')")

        if "path" in package:
            raise HTTPException(status_code=400, detail=f"Local path dependencies are not allowed (package '{name}')")

        for wheel in package.get("wheels", []):
            _check_url(wheel.get("url", ""), name)
        
        sdist = package.get("sdist", {})
        if sdist:
            _check_url(sdist.get("url", ""), name)

def _check_url(url: str, package_name: str) -> None:
    if not url:
        return
    parsed = urlparse(url)
    if parsed.scheme not in ("https"):
        raise HTTPException(status_code=400, detail=f"Invalid URL scheme for package '{package_name}' : non-HTTPS URLs are not allowed")
    if parsed.netloc != ALLOWED_HOST:
        raise HTTPException(status_code=400, detail=f"Invalid URL host for package '{package_name}' : only {ALLOWED_HOST} is allowed")

def validate_param(value: str, pattern: re.Pattern, name: str) -> str:
    if not pattern.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid {name}")
    return value

def get_uv_cache_path():
    res = subprocess.run(
        ["uv", "cache", "dir"],
        check=True, capture_output=True, text=True
    ).stdout.strip()
    return res

BASE_DIR = os.getcwd()
UV_CACHE_DIR = get_uv_cache_path()
uv_env = {**os.environ, "UV_CACHE_DIR": UV_CACHE_DIR}

def get_installed_packages() -> dict[str, str]:
    '''
    Parse the pylock.toml file in the current directory and return a dictionary
    where keys are package names and values are their versions.
    '''
    res = {"path": os.getcwd()}
    try:
        with open("pylock.toml", "rb") as f:  # tomllib exige le mode binaire
            data = tomllib.load(f)
    except FileNotFoundError:
        raise OSError("Could not open pylock.toml. Please consider checking if it exists.", res)
    except tomllib.TOMLDecodeError as e:
        raise OSError(f"Invalid TOML in pylock.toml: {e}", res)

    for package in data.get("packages", []):
        name = package.get("name")
        version = package.get("version")
        if name and version:
            res[name] = version

    return res


#Creates a button on the home page to access the information page.
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>Welcome !</h1>
            <a href="/info/">
                <button>View dowloaded packages</button>
            </a>
        </body>
    </html>
    """

@app.post("/hello/")
async def helloWorld():
    return "Hello world"

#This function is temporary and should soon be replaced 
@app.get("/info/")
async def get_info():
    try :
        return get_installed_packages()
    except OSError as e:
        print(e.args[0])
        return e.args[1]
    
#Consider creating something like an API key to avoid anyone to be able to upload a lockfile and make the server download packages on it, which could be a security issue.
#Also add a verification that the uploaded file is indeed a lockfile and not something else, to avoid any potential security issue. For now, we just check that the filename is valid and that it is located in the current directory, but it would be better to check its content as well.
@app.post("/upload/")
async def sync_pylock(
    file: UploadFile,
    hostname: Optional[str] = Form(default="default_host"),
    platform: Optional[str] = Form(default="x86_64-unknown-linux-gnu"),
    python_version: Optional[str] = Form(default="3.14")
):
    with tempfile.TemporaryDirectory() as tmpdir:

        local_file_path = os.path.join(tmpdir, "pylock.toml")
        platform = validate_param(platform, PLATFORM_RE, "platform")
        python_version = validate_param(python_version, VERSION_RE, "python_version")
        safe_hostname = validate_param(hostname, re.compile(r'^[a-zA-Z0-9_\-]+$'), "hostname")
        tmp_venv = os.path.join(tmpdir, f"venv_{safe_hostname}")

        try:
            content = await file.read(MAX_LOCKFILE_SIZE + 1)
            if len(content) > MAX_LOCKFILE_SIZE:
                raise HTTPException(status_code=400, detail="Lockfile is too large (max 1 MB)")
            validate_lockfile(content)

            # Copy the content of the posted lockfile into a brand new lockfile in the current directory
            with open(local_file_path, "wb") as buffer:
                buffer.write(content)

            # Creating the temporary venv in which we will be downloading every needed packages
            subprocess.run(
                ["uv", "venv", "--python", python_version, tmp_venv],
                check=True, env=uv_env, capture_output=True
            )

            # Step 1 : Downloading and indexing the sdist
            subprocess.run(
                ["uv", "pip", "install",
                 "--python", f"{tmp_venv}/bin/python",
                 "--link-mode=copy",
                 "-r", local_file_path],
                check=True, env=uv_env, capture_output=True
            )

            # Step 2 : Installing for the target platform
            subprocess.run(
                ["uv", "pip", "install",
                 "--python", f"{tmp_venv}/bin/python",
                 "--python-platform", platform,
                 "--python-version", python_version,
                 "--link-mode=copy",
                 "--reinstall",
                 "-r", local_file_path],
                check=True, env=uv_env, capture_output=True
            )


        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else "no stderr"
            stdout = e.stdout.decode() if e.stdout else "no stdout"
            raise HTTPException(status_code=500, detail=f"stderr: {stderr}\nstdout: {stdout}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return "Done"
