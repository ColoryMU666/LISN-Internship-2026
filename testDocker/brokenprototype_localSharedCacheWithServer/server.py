from fastapi import FastAPI, UploadFile, HTTPException, Form
import shutil
import os
import subprocess
from typing import Optional

app = FastAPI()
info = ["a"]

BASE_DIR = os.getcwd()
UV_CACHE_DIR = os.path.expanduser("~/.cache/uv")
uv_env = {**os.environ, "UV_CACHE_DIR": UV_CACHE_DIR}


@app.post("/info/")
async def set_info(file: UploadFile):
    content = await file.read()
    info[0] = content.decode('utf-8').strip()
    return

@app.get("/info/")
async def get_info():
    return {"message": info[0]}

@app.post("/upload/")
async def sync_pylock(
    file: UploadFile,
    #Work only on my machine for the purpose of debugging
    #Should not be needed in the myDocker implementation because every container will share the same base image
    platform: Optional[str] = Form(default="x86_64-unknown-linux-gnu"),
    python_version: Optional[str] = Form(default="3.14")
):
    local_file_path = os.path.join(BASE_DIR, file.filename)

    try:
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        #Creation of a temporary virtual environment to force uv to download the requested packages in the
        #uv cache
        tmp_venv = f"/tmp/venv_{info[0].strip()}"
        subprocess.run(
            #Ideally python version will no be precised here because every container (server and clients) will
            #use the same python version
            f"uv venv --python 3.14 {tmp_venv}",
            shell=True, check=True, env=uv_env, capture_output=True
        )

        #Installation of the requested packages
        subprocess.run(
            f"uv pip install --python {tmp_venv}/bin/python "
            f"--link-mode=copy "
            f"-r pylock.toml",
            shell=True, check=True, capture_output=True, env=uv_env
        )

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "no stderr"
        stdout = e.stdout.decode() if e.stdout else "no stdout"
        raise HTTPException(status_code=500, detail=f"stderr: {stderr}\nstdout: {stdout}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        #Removal of the temporary virtual environment created to force the installation of the package
        #in the uv cache
        subprocess.run(f"rm -rf {tmp_venv}", shell=True)

    return "Done"