FROM ghcr.io/astral-sh/uv:python3.14-dhi

WORKDIR /app

COPY ./server.py .

CMD [ "uv", "run", "--with", "uvicorn", "--with", "fastapi", "--with", "python-multipart", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000" ]