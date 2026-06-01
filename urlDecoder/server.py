from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import subprocess

app = FastAPI()

@app.get("/hello/")
def hello():
    return {"message" : "Hello world"}

@app.get("/")
def fn(git_url=""):
    return{"url" : git_url}
