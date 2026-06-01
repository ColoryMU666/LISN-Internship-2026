from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import subprocess

app = FastAPI()

@app.get("/hello/")
def hello():
    return {"message" : "Hello world"}

@app.get("/", response_class=RedirectResponse)
def fn(git_url=""):
    return RedirectResponse(url="https://github.com/ColoryMU666/LISN-Internship-2026.git", status_code=302)