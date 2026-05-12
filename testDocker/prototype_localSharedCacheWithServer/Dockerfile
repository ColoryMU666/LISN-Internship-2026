FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --system requests

RUN useradd -m -u 1000 appuser

WORKDIR /home/appuser/app

RUN chown -R  appuser:appuser /home/appuser

COPY --chown=appuser:appuser requestPackage.py .

USER appuser

CMD [ "bash" ]