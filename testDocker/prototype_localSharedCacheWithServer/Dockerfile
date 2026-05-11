FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --system requests

WORKDIR /app

RUN uv init
RUN uv add pandas

COPY requestPackage.py .

CMD [ "bash" ]