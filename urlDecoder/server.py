from fastapi import FastAPI
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

@app.get("/", response_class=RedirectResponse, status_code=302)
def fn(shared_cache="", url=""):
    global jupyter_process
    if jupyter_process is None or jupyter_process.poll() is not None:
        jupyter_process = subprocess.Popen("uv run --with nbgitpuller --with jupyterlab jupyter-lab --ip 0.0.0.0 --port 8080 --allow-root", shell=True)
    if wait_for_port(port=8080, timeout=30):
        return url
    else:
        {"error" : "Jupyterlab did not start in time"}