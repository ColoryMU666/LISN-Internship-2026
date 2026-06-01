from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import subprocess

app = FastAPI()

@app.get("/hello/")
def hello():
    return {"message" : "Hello world"}

@app.get("/", response_class=RedirectResponse, status_code=302)
def fn(shared_cache=""):
    subprocess.run("uv run --with nbgitpuller --with jupyterlab jupyter-lab --port 8080", shell=True)
    return "http://localhost:8080/lab"