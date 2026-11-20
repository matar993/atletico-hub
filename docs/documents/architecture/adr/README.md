# Architecture Decision Records

Decisions that span the whole project, one file per decision. Decisions that belong to a single piece of work live in the `design.md` of its OpenSpec change. New ADRs are written with the `architecture-decision-records` skill, or by hand from the skill template [template.md](../../../../.agents/skills/architecture-decision-records/templates/template.md).

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-develop-branch-with-release-branches.md) | `develop` branch with release branches | accepted | 2026-11-05 |
| [0002](0002-backend-on-python-fastapi-and-postgres.md) | The backend is a Python FastAPI app on Postgres | accepted | 2026-11-05 |
| [0003](0003-web-app-is-a-react-spa-on-vite.md) | The web app is a React single-page app on Vite, with a generated API client | accepted | 2026-11-05 |
| [0004](0004-web-app-ships-as-its-own-image-and-reaches-the-api-under-api.md) | The web app ships as its own image and reaches the API on its own origin, under `/api` | accepted | 2026-11-05 |
| [0005](0005-database-access-through-sqlalchemy-and-alembic.md) | The API reaches Postgres through synchronous SQLAlchemy 2, with Alembic migrations | accepted | 2026-11-16 |
| [0006](0006-layered-feature-packages-in-the-api.md) | Each API feature is a package of layers: router, service, schemas, repository, models | accepted | 2026-11-20 |
| [0007](0007-email-and-password-login-with-personal-invite-links.md) | Users sign in with email and password; accounts come only from personal invite links; sessions live in Postgres | accepted | 2026-11-20 |
| [0008](0008-permissions-in-code-checked-on-every-route.md) | Routes check permissions mapped from roles in code; answers carry the actions the user may take on each resource | accepted | 2026-11-20 |
