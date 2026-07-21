"""FastAPI server for launching different instances with specified environments and resource repositories."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import os
import socket
import time
import subprocess
import re
from urllib.parse import quote

# Regular expressions for validating branch names, repository URLs, and base URLs
BRANCH_RE = re.compile(r'^[A-Za-z0-9._/-]+$')
REPO_URL_RE = re.compile(r'^https://[A-Za-z0-9._-]+/[A-Za-z0-9._/-]+(\.git)?$')
URL_RE = re.compile(r"^https://\{\{HOST\['\d{1,5}'\]\}\}/?$")

CLONE_TIMEOUT = 60        # seconds, for the git clone operation
INSTALL_TIMEOUT = 300     # seconds, for uv/pixi install operations

app = FastAPI()

jupyter_process = None

def validate_branch(branch: str) -> str:
    """Validate that a branch name only contains safe characters.

    Args:
        branch: The branch name to validate.

    Returns:
        The validated branch name.

    Raises:
        HTTPException: If the branch name is invalid.

    """
    if not BRANCH_RE.match(branch):
        raise HTTPException(status_code=400, detail="Invalid branch name")
    return branch

def validate_repo_url(repo: str) -> str:
    """Validate that a repository URL uses HTTPS and a safe character set.

    Args:
        repo: The repository URL to validate.

    Returns:
        The validated repository URL.

    Raises:
        HTTPException: If the repository URL is invalid.

    """
    if not REPO_URL_RE.match(repo):
        raise HTTPException(status_code=400, detail="Invalid repository URL")
    return repo

def validate_url(url: str) -> str:
    """Validate that the base URL matches the expected templated host format.

    Args:
        url: The base URL to validate, expected in the form
            `https://{{HOST['<port>']}}` where only the port number varies.

    Returns:
        The validated URL.

    Raises:
        HTTPException: If the URL does not match the expected format.

    """
    if not URL_RE.match(url):
        raise HTTPException(status_code=400, detail="Invalid url format")
    return url

def wait_for_port(port : int, timeout : int = 30) -> bool:
    """Wait for a port to be open on localhost.

    Args:
        port: The port to wait for.
        timeout: The maximum time to wait in seconds.

    Returns:
        True if the port is open, False if the timeout was reached.

    """
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
    """Return a simple greeting. Used for debugging purposes.

    Returns:
        A dictionary with a greeting message.

    """
    return {"message" : "Hello world"}

@app.get("/launch/", response_class=RedirectResponse, status_code=302)
def launchApp(request : Request):
    """Launch a JupyterLab instance with the specified environment and resource repositories.

    Currently the only app available is JupyterLab, but this will be extended in the future to support other applications.

    Args:
        request: The incoming HTTP request containing query parameters.

    Returns:
        A redirect response to the JupyterLab instance.

    Raises:
        RuntimeError: If JupyterLab does not start within the timeout period.

    """
    # Extract query parameters from the request
    params = request.query_params

    url = validate_url(params.get("url", ""))
    token = params.get("token", "")
    envRepo = validate_repo_url(params.get("envRepo", ""))
    envBranch = validate_branch(params.get("envBranch", "main"))
    ressourceRepo = validate_repo_url(params.get("ressourceRepo", ""))
    ressourceBranch = validate_branch(params.get("ressourceBranch", "main"))
    urlPath = params.get("urlPath", "")

    global jupyter_process

    try:
        # Clone the environment repository into a temporary directory
        subprocess.run(
            ["git", "clone", "--branch", envBranch, "--", envRepo, "tmp/env"],
            check=True, timeout=CLONE_TIMEOUT
        )

        # Look for dependency files and install dependencies accordingly
        if os.path.exists("tmp/env/pyproject.toml"):  # For uv project
            print("Installing dependencies from pyproject.toml")
            subprocess.run(["uv", "sync"], check=True, timeout=INSTALL_TIMEOUT)

        if os.path.exists("tmp/env/requirements.txt"):  # For uv project
            print("Installing dependencies from requirements.txt")
            subprocess.run(
                ["uv", "pip", "install", "-r", "tmp/env/requirements.txt"],
                check=True, timeout=INSTALL_TIMEOUT
            )

        if os.path.exists("tmp/env/environment.yml"):  # For pixi project
            print("Installing dependencies from environment.yml")
            subprocess.run(
                ["pixi", "init", "--import", "tmp/env/environment.yml"],
                check=True, timeout=INSTALL_TIMEOUT
            )
            subprocess.run(["pixi", "install"], check=True, timeout=INSTALL_TIMEOUT)

    except subprocess.TimeoutExpired as e:
        raise HTTPException(
            status_code=504,
            detail=f"Command timed out after {e.timeout}s: {' '.join(e.cmd)}"
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Command failed (exit code {e.returncode}): {' '.join(e.cmd)}"
        )

    can_return = True

    # Get the last part of the resource repository path to construct the URL path if we don't have a specific urlPath provided (should be removed in the future)
    try:
        buff = ""
        i = len(ressourceRepo)-1
        while ressourceRepo[i] != "/":
            buff += ressourceRepo[i]
            i -= 1
        buff = buff[::-1]
    except IndexError:
        can_return = False
    
    # Start the JupyterLab process if it's not already running
    if jupyter_process is None or jupyter_process.poll() is not None:
        jupyter_process = subprocess.Popen([
            "uv", "run", "--with", "nbgitpuller", "--with", "jupyterlab",
            "jupyter-lab", "--ip", "0.0.0.0", "--port", "8080",
            f"--IdentityProvider.token={token}", "--allow-root", "--no-browser"
        ])
    # Wait for the JupyterLab server to start and listen on port 8080
    if wait_for_port(port=8080, timeout=30):
        pass
    else:
        raise RuntimeError("JupyterLab did not start within the timeout period.")

    # Construct the redirect URL based on the provided parameters and return it
    if can_return and urlPath == "":
        return (
            f"{url}git-pull?"
            f"token={quote(token, safe='')}"
            f"&repo={quote(ressourceRepo, safe='')}"
            f"&branch={quote(ressourceBranch, safe='')}"
            f"&urlPath={quote(f'lab/tree/{buff}/', safe='/')}"
        )
    elif can_return:
        return (
            f"{url}git-pull?"
            f"token={quote(token, safe='')}"
            f"&repo={quote(ressourceRepo, safe='')}"
            f"&branch={quote(ressourceBranch, safe='')}"
            f"&urlPath={quote(urlPath, safe='/')}"
        )

@app.get("/debug/")
def debug(request: Request):
    """Debug endpoint to print the raw URL and query parameters.

    Args:
        request: The incoming HTTP request.

    Returns:
        A dictionary containing the raw request URL and the parsed query parameters.

    """
    return {"url": str(request.url), "params": dict(request.query_params)}
    
    