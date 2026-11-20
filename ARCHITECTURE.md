# Architecture

How Atletico Hub is built today. The decisions behind it, with their rejected alternatives, are in [docs/documents/architecture/adr/](docs/documents/architecture/adr/README.md); the current behavior of each capability is in [openspec/specs/](openspec/specs).

## Overview

Atletico Hub is a web app with a separate API. The browser loads the web app from its own image and reaches the API through it, under `/api` ([ADR-0004](docs/documents/architecture/adr/0004-web-app-ships-as-its-own-image-and-reaches-the-api-under-api.md)). The API keeps the data in Postgres.

```mermaid
flowchart LR
    browser(["Browser"])

    subgraph web["Image atletico-hub-web"]
        spa["React SPA<br/>frontend/<br/>/api proxy: Vite (dev), nginx (prod)"]
    end

    subgraph api["Image atletico-hub-api"]
        app["FastAPI app<br/>backend/src/atletico_hub<br/>(atletico_hub.main:app)"]
    end

    db[("Postgres")]

    browser --> spa
    spa -- "/api/*" --> app
    app --> db
```

## Components

| Component | Code | Responsibility |
|---|---|---|
| Web app | `frontend/` | Pages for players and staff; calls the API through the generated client `frontend/src/lib/api/` ([ADR-0003](docs/documents/architecture/adr/0003-web-app-is-a-react-spa-on-vite.md)) |
| API | `backend/src/atletico_hub/` | HTTP routes, business rules, access to the database ([ADR-0002](docs/documents/architecture/adr/0002-backend-on-python-fastapi-and-postgres.md)) |
| Database access | `backend/src/atletico_hub/db/` | Settings, engine, per-request session (`get_session`), declarative `Base`, Alembic migrations ([ADR-0005](docs/documents/architecture/adr/0005-database-access-through-sqlalchemy-and-alembic.md)) |
| Database | Postgres | The team's data; its schema changes only through migrations |

## Boundaries

- The web app reaches the API only through `/api` on its own origin, and only through the generated client.
- The API is the only component that reads or writes the database.
- Inside the API, each feature is a package of layers: router, service, schemas, repository, models ([ADR-0006](docs/documents/architecture/adr/0006-layered-feature-packages-in-the-api.md)). A layer imports only the layers below it, and only the router knows HTTP. `import-linter` checks both rules in CI.
- Features reach the database through their repositories, which wrap the session of `get_session`. Routes never run queries. The service holds the business rules and commits the transaction.
- Business rules live in the API. The web app checks input for usability only; the API checks it again.
- Code is grouped by feature, not by kind ([CODE_GUIDELINES.md](CODE_GUIDELINES.md#code-patterns)).

## Today

The app holds only the skeleton: the API answers `GET /health` and the web app shows the home page. The database layer is in place, with no table yet. Each feature arrives as an OpenSpec change, which updates this document when it changes the components or their boundaries.
