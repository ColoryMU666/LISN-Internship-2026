from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
import shutil
import os
import subprocess
import shlex
import re
import tempfile
from typing import Optional

PLATFORM_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
VERSION_RE  = re.compile(r'^\d+\.\d+(\.\d+)?$')

app = FastAPI()

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
    This function parse the pylock.toml file in the current directory and return a dictionnary where the
    keys are the name of the package needed and the values are their version.
    '''
    readName = False
    reading = False
    name = ""
    res = {"path" : os.getcwd()}
    try:
        file = open("pylock.toml", "r")
    except:
        raise OSError("Could not open pylock.toml. Please consider checking if it exists.", res)
    for line in file:
        if not readName and reading:
            res[name] = line[11:-2]
            reading = False
        if readName and reading:
            name = line[8:-2]
            readName = False
        if line.startswith("[[packages]]"):
            readName = True
            reading = True
    file.close()
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
    
# Consider creating something like an API key to avoid anyone to be able to upload a lockfile and make the server download packages on it, which could be a security issue.
# Also add a verification that the uploaded file is indeed a lockfile and not something else, to avoid any potential security issue.
# For now, we just check that the filename is valid and that it is located in the current directory, but it would be better to check its content as well.
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
            # Copy the content of the posted lockfile into a brand new lockfile in the current directory
            with open(local_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

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
