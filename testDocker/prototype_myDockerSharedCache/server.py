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

@app.post("/hello/")
async def helloWorld():
    return "Hello world"

# Change the two following function to support several demands at the same time. Currently if 
# A, B and C asks for their env and the info request is processed quicker than the upload request 
# the created venv for B will be named venv_C. It's not much of a problem but it would be better 
# for clarity and debugging purpose if the venv always have the name of the machinie who requested it.
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
    platform: Optional[str] = Form(default="x86_64-unknown-linux-gnu"),
    python_version: Optional[str] = Form(default="3.14")
):
    local_file_path = os.path.join(BASE_DIR, file.filename)

    try:
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        tmp_venv = f"/tmp/venv_{info[0].strip()}"
        subprocess.run(
            f"uv venv --python 3.14 {tmp_venv}",
            shell=True, check=True, env=uv_env, capture_output=True
        )

        # Passe 1 : télécharger et indexer les sdists nativement
        subprocess.run(
            f"uv pip install --python {tmp_venv}/bin/python "
            f"--link-mode=copy "
            f"-r pylock.toml",
            shell=True, check=True, capture_output=True, env=uv_env
        )

        # Passe 2 : installer pour la plateforme cible
        subprocess.run(
            f"uv pip install --python {tmp_venv}/bin/python "
            f"--python-platform {platform} "
            f"--python-version {python_version} "
            f"--link-mode=copy "
            f"--reinstall "
            f"-r pylock.toml",
            shell=True, check=True, capture_output=True, env=uv_env
        )

        subprocess.run(f"rm -rf {tmp_venv}", shell=True)


    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "no stderr"
        stdout = e.stdout.decode() if e.stdout else "no stdout"
        raise HTTPException(status_code=500, detail=f"stderr: {stderr}\nstdout: {stdout}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return "/tmp/tosend.zip"
