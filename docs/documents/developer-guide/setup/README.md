# Setup and development

How to configure, start and develop the app locally.

> **Source**: `Makefile`, `compose.yaml`, `.githooks/pre-commit`, `.github/workflows/ci.yml`
> **Last update**: 2026-11-05 · **Scope**: local stack, commands, checks, worktrees, dependencies · **Markers**: none

## Prerequisites

- Docker with Docker Compose
- [uv](https://docs.astral.sh/uv/): installs the Python version of `backend/.python-version` (3.14)
- Node 22 (`frontend/.nvmrc`), only for the browser tests on the host
- OpenSpec CLI: `npm install --global @fission-ai/openspec`
- [gh](https://cli.github.com/), signed in with `gh auth login`, for pull requests

## First setup

Run once per clone:

```bash
cp example.env .env   # optional: the defaults work without it
make hooks            # installs the pre-commit hook of .githooks/
cd backend && uv sync # the backend environment for lint, format and type checks on the host
```

On Windows, enable symlinks before cloning: `CLAUDE.md` and `.claude/skills` are symlinks.

```bash
git config --global core.symlinks true
```

## Start the stack

```bash
make up   # builds and starts Postgres, API and web app
```

- Web app: http://127.0.0.1:3200
- API: http://127.0.0.1:8200 (`/docs`, `/health`); the web app reaches it under `/api` ([ADR-0004](../../architecture/adr/0004-web-app-ships-as-its-own-image-and-reaches-the-api-under-api.md))
- Postgres: `127.0.0.1:5434`

Other stack commands:

```bash
make ps     # services and ports
make logs   # follow the logs
make down   # stop everything; the volumes are kept
```

### Notes

- Edits to `backend/src/atletico_hub/` reload the API without a rebuild. Edits to `frontend/` reload the web app.
- After a new backend dependency, run `docker compose build api`.
- To start from an empty database, run `docker compose down -v`: it also deletes the volumes.
- `example.env` lists the variables you can set.
- When the web app does not reload on file changes, set `VITE_POLLING=1` in `.env`.

## Technology stack

- **Backend**: Python 3.14, FastAPI, Pydantic, uv; Postgres; pytest, ruff, ty ([ADR-0002](../../architecture/adr/0002-backend-on-python-fastapi-and-postgres.md))
- **Web app**: React, TypeScript, Vite, TanStack Router and Query, Tailwind CSS, `openapi-fetch`; Vitest, Playwright, ESLint, Prettier ([ADR-0003](../../architecture/adr/0003-web-app-is-a-react-spa-on-vite.md))
- **Tooling**: OpenSpec for specs, Docker Compose for the local stack, GitHub Actions for CI

## Commands and checks

| Scope | Command | Description |
|---|---|---|
| start stack | `make up` | Build and start Postgres, API and web app |
| backend tests | `make test` | pytest with coverage in a one-off `api` container; fails below 90% |
| backend lint | `make lint` | ruff check |
| backend lint fix | `make lint-fix` | ruff check with the safe fixes |
| backend format | `make autoformat` | ruff format |
| backend types | `make typecheck` | ty check |
| lock | `make lock` | Regenerate `backend/uv.lock` ([details](#backend-dependencies)) |
| specs | `make validate` | `openspec validate --all --strict` |
| web app checks | `make ui-checks` | Type check, lint, format check, unit tests and build |
| web app format | `make ui-format` | Rewrite the web app files with Prettier |
| browser tests | `make ui-e2e` | Playwright, on the host |
| API types | `make ui-gen-api` | Regenerate the web app's API types ([details](#web-app-development)) |

`lint`, `lint-fix`, `autoformat` and `typecheck` need only uv. The `ui-*` targets other than `ui-e2e` run in the `ui` container, so the stack must be up. `ui-e2e` needs no stack.

### Pre-commit hook

`make hooks` installs it once per clone. It runs the checks of the areas a commit touches:

- `openspec/`: `make validate`
- `backend/`: ruff lint with the safe fixes, ruff format, ty
- `frontend/`: lint, format check, unit tests and build
- `backend/` or `frontend/`: `schema.d.ts` matches the API

The backend and web app checks need the stack up. The hook is a last-chance safety net: run the checks of the [Definition of Done](../../../../CONTRIBUTING.md#definition-of-done) before committing. Skip it once with `git commit --no-verify`.

### Running a subset of the backend tests

```bash
docker compose run --rm api pytest tests/unit
docker compose run --rm api pytest tests -k "health" -v
```

Test layout and rules: [CODE_GUIDELINES.md](../../../../CODE_GUIDELINES.md#tests).

### CI

`.github/workflows/ci.yml` runs on every pull request and on pushes to `develop`, `release/**` and `v*` tags. A paths filter runs only the jobs of the areas a change touches:

| Job | Runs on changes to | Does |
|---|---|---|
| `openspec-validate` | `openspec/` | `openspec validate --all --strict` |
| `backend-checks` | `backend/` | ruff check, ruff format check, ty |
| `backend-tests` | `backend/` | pytest with coverage, against a Postgres service |
| `ui-checks` | `frontend/` | type check, lint, format check, unit tests, build |
| `ui-e2e` | `frontend/` | Playwright on the production build, in the Playwright image of the locked version |
| `ui-api-types` | `backend/` or `frontend/` | `schema.d.ts` matches the API's OpenAPI document |
| `images` | `backend/` or `frontend/` | builds the API and web app images |
| `ci-ok` | always | fails when any job failed or was cancelled |

`ci-ok` is the only required check of the branch protection: a change to documents only runs no job, and `ci-ok` still passes.

## Worktrees

A Git worktree gives a second checkout of the repository, with two branches open at once. Create one from `develop` with `git worktree add ../atletico-hub-<topic> -b <type>/<topic> origin/develop`. After the merge, remove it with `git worktree remove ../atletico-hub-<topic>`, `git worktree prune` and `git branch -d <type>/<topic>` (use `-D` when the squash merge leaves the branch looking unmerged).

Each worktree needs its own `.env`: the file is ignored by Git, copy it from the main checkout. The stack is shared: `compose.yaml` fixes the project name (`atletico-hub`) and the published ports (3200, 8200, 5434), so the host runs one stack at a time.

- `make up` in a second worktree recreates the services on the sources of that worktree. The data stays.
- `make down` stops the stack from any worktree.
- Lint, format and type checks, and `make validate`, need only the worktree itself.

## Web app development

The web app calls the API on its own origin, under `/api` ([ADR-0004](../../architecture/adr/0004-web-app-ships-as-its-own-image-and-reaches-the-api-under-api.md)). In development the Vite server proxies `/api` to the `api` container.

- Routes are files in `frontend/src/routes/`. The Vite plugin regenerates `frontend/src/routeTree.gen.ts`: commit it.
- API calls go through `frontend/src/lib/api/client.ts`, typed by `frontend/src/lib/api/schema.d.ts`. After changing a route of the API, run `make ui-gen-api` and commit the result.
- After changing `frontend/package.json`, the `ui` container installs the dependencies again on its next start (`docker compose restart ui`).

The image builds with `docker build -t atletico-hub-web frontend`. `API_UPSTREAM` is the API's origin only: scheme, host and port, no path.

## Backend dependencies

`backend/pyproject.toml` declares the dependencies and the development tools. `backend/uv.lock` is the only lock, used by the host, the images and CI. After changing dependencies, run:

```bash
make lock
cd backend && uv sync
docker compose build api
```
