from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import subprocess

app = FastAPI()

@app.post("/hello/")
def hello():
    return {"message" : "Hello world"}

#@app.post("/")
#def func(git_url, token, server_url=""):
#    git_url = f"https://{git_url}"
#    subprocess.run(f"uvx --with nbgitpuller --from jupyterlab sh -c \"gitpuller {git_url} main jserv && jupyter-lab --no-browser --ip=\"0.0.0.0\" --IdentityProvider.token={token} --allow-root jserv\"", shell=True)
#    return
