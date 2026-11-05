# Architecture Decision Records

Decisions that span the whole project, one file per decision. Decisions that belong to a single piece of work live in the `design.md` of its OpenSpec change. New ADRs are written with the `architecture-decision-records` skill, or by hand from the skill template [template.md](../../../../.agents/skills/architecture-decision-records/templates/template.md).

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-develop-branch-with-release-branches.md) | `develop` branch with release branches | accepted | 2026-11-05 |
| [0002](0002-backend-on-python-fastapi-and-postgres.md) | The backend is a Python FastAPI app on Postgres | accepted | 2026-11-05 |
| [0003](0003-web-app-is-a-react-spa-on-vite.md) | The web app is a React single-page app on Vite, with a generated API client | accepted | 2026-11-05 |
| [0004](0004-web-app-ships-as-its-own-image-and-reaches-the-api-under-api.md) | The web app ships as its own image and reaches the API on its own origin, under `/api` | accepted | 2026-11-05 |
