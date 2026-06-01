from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import subprocess

app = FastAPI()

@app.get("/hello/")
def hello():
    return {"message" : "Hello world"}

@app.get("/", response_class=RedirectResponse, status_code=302)
def fn(git_url=""):
    return git_url