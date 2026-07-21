# JupyterLab Environment Launcher

A lightweight FastAPI backend that provisions an on-demand JupyterLab
working environment in response to an incoming HTTP request. It is designed
to be called by **JupyterHub**, as the target of an
[`nbgitpuller`](https://github.com/jupyterhub/nbgitpuller)-style invitation
link: an authenticated user clicks a link, a dedicated container running
this service is spawned for them, and the service builds a ready-to-use
JupyterLab instance on the fly (dependencies installed, resource repository
cloned) before redirecting the user into it.

## Companion project

This project works hand in hand with
[`linkGenerator`](https://gitlab.dsi.universite-paris-saclay.fr/matthieu.urios/linkGenerator):
that repository is responsible for **generating** the invitation/classic
links (through an interactive MyST form), while this repository is
responsible for **decoding** those links on the receiving end, before the
request is forwarded to the actual launcher service. The two projects must
stay in sync: any field added or changed on the generation side should be
reflected in how this project parses the resulting link.

## Deployment model

- Each user is given their **own container** running this service. There is
  never more than one active request/session per running instance, so
  module-level state (the temporary working directory, the JupyterLab
  process handle) is safe by construction — it is never shared across
  users.
- Authentication happens **upstream** before
  a container is ever spawned or a request reaches this service. An
  unauthenticated user cannot cause an environment to start.
- Because each user's environment is isolated to their own container, users
  are free to point `envRepo` / `ressourceRepo` at any HTTPS Git repository
  they like — this only affects their own environment. There is currently
  no shared package cache; that is planned separately (see [Roadmap](#roadmap)) and
  will introduce its own restrictions when implemented.

## What it does

When a request hits `/launch/`, the service:

1. Validates the request parameters (see Query parameters below).
2. Cleans up any previous temporary working directory (`tmp/`) and creates a
   fresh one.
3. Clones the requested **environment repository** (`envRepo` /
   `envBranch`) into `tmp/env`.
4. Installs the dependencies described in that repository, based on which
   manifest file is present:
   - `pyproject.toml` -> `uv sync`
   - `requirements.txt` -> `uv pip install -r requirements.txt`
   - `environment.yml` -> `pixi init --import` + `pixi install`
5. Starts (or reuses, if already running in this container) a `jupyter-lab`
   process on port `8080`, protected by the provided token, launched via
   `uv run --with nbgitpuller --with jupyterlab`.
6. Waits for the JupyterLab server to be reachable on port `8080`.
7. Builds and returns a redirect URL pointing at nbgitpuller's `git-pull`
   endpoint, so the **resource repository** (`ressourceRepo` /
   `ressourceBranch`) is pulled into the freshly started JupyterLab and
   opened at the right path.

In short: clicking one invitation link spins up a dedicated, isolated
container that turns a pair of Git repositories (one for the environment,
one for the working resources/notebooks) into a running, pre-configured
JupyterLab session.

## API Endpoints

| Method | Path       | Purpose                                                                 |
|--------|------------|--------------------------------------------------------------------------|
| GET    | `/hello/`  | Simple health/debug check, returns a greeting message.                  |
| GET    | `/launch/` | Main endpoint: provisions the environment and redirects to JupyterLab.  |
| GET    | `/debug/`  | Returns the raw request URL and query parameters as JSON (debugging).   |

### `/launch/` query parameters

| Parameter          | Required | Default                        | Validation                                                       |
|--------------------|----------|---------------------------------|--------------------------------------------------------------------|
| `url`               | yes      | -                                | Must match the templated host form `https://{{HOST['<port>']}}`.  |
| `token`             | yes      | -                                | Used both to secure JupyterLab and for the redirect; not restricted in format. |
| `envRepo`           | yes      | -                                | Must be an HTTPS Git URL (any host - see Deployment model above). |
| `envBranch`         | no       | `main`                           | Restricted to a safe character set (`[A-Za-z0-9._/-]+`).          |
| `ressourceRepo`     | yes      | -                                | Must be an HTTPS Git URL (any host).                               |
| `ressourceBranch`   | no       | `main`                           | Restricted to a safe character set (`[A-Za-z0-9._/-]+`).          |
| `urlPath`           | no       | *(derived from `ressourceRepo`)* | Not restricted; already URL-encoded by the calling link generator where needed. |

Invalid values for `url`, `envRepo`, `ressourceRepo`, `envBranch`, or
`ressourceBranch` cause the request to fail with `HTTP 400` rather than
being passed on to `git`/`uv`/`pixi`.

## Requirements

- Python 3 with [`uv`](https://docs.astral.sh/uv/) available on `PATH`.
- [`pixi`](https://pixi.sh/) available on `PATH` if `environment.yml`-based
  environments are to be supported.
- `git` available on `PATH`.
- Network access to the environment/resource Git repositories.

## Security notes

- **Command execution**: all `git`/`uv`/`pixi` calls are run without a
  shell (`shell=True` is never used) and with argument lists, so query
  parameters cannot be interpreted as shell syntax. `git clone` also uses
  `--` to prevent a crafted `envRepo` value from being parsed as a `git`
  option.
- **Open redirect**: the `url` parameter is validated against a strict
  template (`https://{{HOST['<port>']}}`) rather than accepted as an
  arbitrary redirect target.
- **Redirect URL encoding**: `token`, `ressourceRepo`, `ressourceBranch`,
  and `urlPath` are URL-encoded before being inserted into the generated
  redirect URL, to avoid a crafted value altering the structure of that
  URL. `urlPath` preserves `/` characters (`safe='/'`) since it encodes a
  path; the other values do not.
- **Timeouts**: `git clone`, `uv sync`/`uv pip install`, and `pixi
  init`/`pixi install` all run with an explicit timeout and their failures
  are reported as a clean `HTTP 500`/`504` instead of hanging the request
  indefinitely.
- **Accepted residual risk**: since `envRepo`/`ressourceRepo` accept any
  HTTPS host and this container can reach the university's internal
  network, an authenticated user could in principle use their own container
  to reach internal HTTPS endpoints under the guise of "cloning a repo".
  This is accepted for now given the per-user container isolation and
  upstream authentication - flag if this assumption ever changes (e.g. if
  containers gain broader network access than intended).

## Roadmap

- Support launching applications other than JupyterLab, and allow passing
  a custom startup command for the environment.
- Introduce a shared package cache (see the companion cache service) to
  reduce redundant downloads across environments, which will come with its
  own source restrictions.

## Adding to this project

See [`CONTRIB.md`](./CONTRIB.md) for guidelines on contributing to this
project and for what should be added next.