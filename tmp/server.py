from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app =  FastAPI()

@app.get("/test/", response_class=PlainTextResponse)
def fn(request: Request):
    return f"RAW URL: {request.url}\nPARAMS: {dict(request.query_params)}"
     
