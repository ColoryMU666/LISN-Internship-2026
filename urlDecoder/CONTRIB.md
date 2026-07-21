# Contributing to this project

This document is meant for whoever picks up this codebase next. It explains
how the `/launch/` endpoint is meant to be extended, and lists what is
currently known to be missing or incomplete.

## How to keep developing

Everything currently happens inside the `/launch/` endpoint.

### Adding a new parameter

1. Read it from `request.query_params`, the same way the existing
   parameters (`envRepo`, `envBranch`, `token`, ...) are read.
2. Ask yourself whether this parameter could lead to unsafe behavior if a
   user sent an unexpected or malicious value (e.g. it gets passed to a
   subprocess, used to build a file path, used to build a redirect URL,
   etc.).
   - If **yes**: write a small `validate_xxx(value: str) -> str` function
     (see `validate_branch`, `validate_repo_url`, `validate_url` for
     examples) that either returns the value unchanged or raises an
     `HTTPException(status_code=400, ...)`. Call it right where the
     parameter is read, the same way the existing parameters are validated.
   - If **no** (the value never reaches a subprocess, a file path, or a
     URL construction — e.g. it's only used for logging or display),
     validation can be skipped, but double check that assumption stays
     true as the code evolves.

### Running commands

- **Never use `shell=True`** when calling `subprocess.run`/`subprocess.Popen`.
  Always pass the command as a list of arguments
  (`["git", "clone", "--branch", branch, "--", repo, "dest"]`, not a single
  formatted string). This is what prevents shell injection through query
  parameters — do not reintroduce string-formatted shell commands even for
  something that looks like a quick fix.
- If you add a command whose arguments could otherwise be confused with
  flags (like `git clone` and its `--` before the repo URL), check whether
  the tool you are calling supports a similar `--` separator, and use it.

### Containers and ports

Keep in mind that every instance of this service runs inside its own Docker
container, dedicated to a single authenticated user. The general pattern for
launching an application is and should remain:

1. Start the application so that it listens on a port inside the container.
2. Wait for that port to become reachable (see `wait_for_port`).
3. Redirect the user to that port (through `git-pull`/nbgitpuller for
   JupyterLab today, or directly to the port for other applications in the
   future).

Any new application you make launchable through this service should follow
this same "start it in the container, expose a port, redirect to it"
pattern rather than inventing a different mechanism per application.

## What's left to do

- **Support more applications.** Only JupyterLab can be launched today. The
  launch logic (steps 5-7 in the README) is written specifically for
  JupyterLab and will need to be generalized (e.g. a small mapping of
  "app name" -> "how to start it" -> "which port it uses").
- **Split the code.** Currently everything lives in one file. The plan is
  to separate:
  - the FastAPI endpoints into a dedicated `server.py`
  - the validation functions (`validate_branch`, `validate_repo_url`,
    `validate_url`, and any future ones) into their own module.
- **Let the user choose the startup command.** Right now the startup
  command is hardcoded for JupyterLab. Users should eventually be able to
  specify their own startup command through the invitation link. Remember
  this makes the "is this parameter safe" question from the section above
  especially important — a user-supplied command is exactly the kind of
  parameter that needs careful thought before being passed to a subprocess.
- **Reduce the size/exposure of the URL.** All parameters are currently
  passed in clear text in the query string, so anyone able to read the URL
  (browser history, logs, a shoulder-surf) can see every argument. This
  also means the URL will keep growing as more parameters are added, and
  could eventually hit practical URL length limits. Some way of shortening
  or opaquing this URL (e.g. a server-side lookup key instead of raw
  parameters) should be found at some point.