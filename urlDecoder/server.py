from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import socket
import time
import signal
import subprocess

app = FastAPI()

jupyter_process = None

def wait_for_port(port : int, timeout : int = 30) -> bool:
    start = time.time()
    while time.time() - start <= timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

@app.get("/hello/")
def hello():
    return {"message" : "Hello world"}

@app.get("/launchJL/", response_class=RedirectResponse, status_code=302)
def fn(request : Request):
    params = request.query_params
    
    url = params.get("url", "")
    token = params.get("token", "")
    envRepo = params.get("envRepo", "")
    envBranch = params.get("envBranch", "main")
    ressourceRepo = params.get("ressourceRepo", "")
    ressourceBranch = params.get("ressourceBranch", "main")
    urlPath = params.get("urlPath", "")

    global jupyter_process

    os.mkdir("tmp", exist_ok=True)
    subprocess.run(f"git clone --branch {envBranch} {envRepo} tmp/env", shell=True)
    if os.path.exists("tmp/env/requirements.txt"):
        subprocess.run(f"uv pip install -r tmp/env/requirements.txt", shell=True)

    can_return = True
    try:
        buff = ""
        i = len(ressourceRepo)-1
        while ressourceRepo[i] != "/":
            buff += ressourceRepo[i]
            i -= 1
        buff = buff[::-1]
    except IndexError:
        can_return = False
    if jupyter_process is None or jupyter_process.poll() is not None:
        jupyter_process = subprocess.Popen(f"uv run --with nbgitpuller --with jupyterlab jupyter-lab --ip 0.0.0.0 --port 8080 --IdentityProvider.token={token} --allow-root --no-browser", shell=True)

    if wait_for_port(port=8080, timeout=30):
        pass
    else:
        return str(request.url)

    if can_return and urlPath == "":
        return f"{url}git-pull?token={token}&repo={ressourceRepo}&branch={ressourceBranch}&urlPath=lab/tree/{buff}/"
    elif can_return:
        return f"{url}git-pull?token={token}&repo={ressourceRepo}&branch={ressourceBranch}&urlPath={urlPath}"

@app.get("/debug/", response_class=RedirectResponse, status_code=302)
def fn(request: Request):
    print("RAW URL:", request.url)
    print("PARAMS:", dict(request.query_params))
    
    