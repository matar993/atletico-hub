# Atletico Hub

The web app of Atletico San Lorenzo, an 8-a-side football team.

## Architecture

Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how the app is built and which decisions (ADRs) shaped it.

## Quick start

Prerequisites: Docker and Docker Compose.

```bash
make up      # builds and starts Postgres, the API and the web app
make hooks   # once per clone: installs the pre-commit hook
```

Web app: http://127.0.0.1:3200 · API: http://127.0.0.1:8200/docs

Ports, other commands, checks and troubleshooting: [Developer guide](docs/documents/developer-guide/setup/README.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and [CODE_GUIDELINES.md](CODE_GUIDELINES.md) for the code and test rules before submitting changes. Coding agents start from [AGENTS.md](AGENTS.md).

## Other docs

| Document | Read when |
|---|---|
| [Developer guide](docs/documents/developer-guide/setup/README.md) | You set up the stack, run the checks or change dependencies |
| [User guide](docs/documents/user-guide/README.md) | You use the app as a player or as staff |
| [ADRs](docs/documents/architecture/adr/README.md) | You need to know why the app is built a certain way |

## Repository structure

| Folder | Contents |
|---|---|
| `backend/` | The API: the Python package `atletico_hub` (`src/atletico_hub/`), its tests (`tests/`) and its image (`Dockerfile`, `pyproject.toml`, `uv.lock`) ([ADR-0002](docs/documents/architecture/adr/0002-backend-on-python-fastapi-and-postgres.md)) |
| `frontend/` | The web app: React and Vite, its unit and browser tests, and its image (`Dockerfile`, `nginx/`) ([ADR-0003](docs/documents/architecture/adr/0003-web-app-is-a-react-spa-on-vite.md)) |
| `docs/` | `documents/` (`architecture/` with ADRs, `developer-guide/`, `user-guide/`) and `facts/` (verified facts) |
| `openspec/` | [OpenSpec](https://github.com/Fission-AI/OpenSpec): specs of the current behavior (`specs/`) and in-progress and completed changes (`changes/`) |
| `.github/` | CI workflow, pull request and issue templates, Dependabot |
| `.githooks/` | The pre-commit hook, installed with `make hooks` |
| `.agents/skills/` | Skills shared by coding agents; Pi loads them through `.pi/settings.json` (`.claude/skills` points here) |
| `.agents/agents/` | Subagents of the coding agents |
