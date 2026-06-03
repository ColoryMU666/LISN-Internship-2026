from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
import shutil
import os
import subprocess
from typing import Optional

app = FastAPI()
info = ["a"] # Pointeur python

def get_uv_cache_path():
    if os.path.exists("cacheloc.txt"):
        subprocess.run("rm cacheloc.txt", shell=True)
    subprocess.run("echo `uv cache dir` > cacheloc.txt", shell=True)
    file = open("cacheloc.txt", "r")
    for l in file:
        res = l
    subprocess.run("rm cacheloc.txt", shell=True)
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

# Change the following function to support several demands at the same time. Currently if 
# A, B and C asks for their env and the info request is processed quicker than the upload request 
# the created venv for B will be named venv_C. It's not much of a problem but it would be better 
# for clarity and debugging purpose if the venv always have the name of the machine who requested it.
@app.post("/info/")
async def set_info(file: UploadFile):
    content = await file.read()
    info[0] = content.decode('utf-8').strip()
    return

#This function is temporary and should soon be replaced 
@app.get("/info/")
async def get_info():
    try :
        return get_installed_packages()
    except OSError as e:
        print(e.args[0])
        return e.args[1]

@app.post("/upload/")
async def sync_pylock(
    file: UploadFile,
    platform: Optional[str] = Form(default="x86_64-unknown-linux-gnu"),
    python_version: Optional[str] = Form(default="3.14")
):
    local_file_path = os.path.join(BASE_DIR, file.filename)

    try:
        # Copy the content of the posted lockfile into a brand new lockfile in the current directory
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Creating the temporary venv in which we will be downloading every needed packages
        tmp_venv = f"/tmp/venv_{info[0].strip()}"
        subprocess.run(
            f"uv venv --python 3.14 {tmp_venv}",
            shell=True, check=True, env=uv_env, capture_output=True
        )

        # Step 1 : Downloading and indexing the sdist
        subprocess.run(
            f"uv pip install --python {tmp_venv}/bin/python "
            f"--link-mode=copy "
            f"-r pylock.toml",
            shell=True, check=True, capture_output=True, env=uv_env
        )

        # Step 2 : Installing for the target platform
        subprocess.run(
            f"uv pip install --python {tmp_venv}/bin/python "
            f"--python-platform {platform} "
            f"--python-version {python_version} "
            f"--link-mode=copy "
            f"--reinstall "
            f"-r pylock.toml",
            shell=True, check=True, capture_output=True, env=uv_env
        )

        # Remove the temporary venv previously created
        subprocess.run(f"rm -rf {tmp_venv}", shell=True)


    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "no stderr"
        stdout = e.stdout.decode() if e.stdout else "no stdout"
        raise HTTPException(status_code=500, detail=f"stderr: {stderr}\nstdout: {stdout}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return "Done"
