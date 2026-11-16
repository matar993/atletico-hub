# Proposal

## Why

The API has no way to read or write Postgres: no driver, no models, no migrations. Every planned feature needs stored data, starting with `add-auth-and-roles`, so the database layer comes first, in its own reviewable change.

## What Changes

- Add SQLAlchemy 2 (synchronous, psycopg 3 driver) as the API's database access library.
- Add Alembic for versioned schema migrations, shipped inside the `atletico_hub` package so the API image can run them.
- Add database settings read from the existing `DB_*` environment variables.
- Add a per-request database session, provided as a FastAPI dependency.
- Run the migrations to the latest revision before the API starts, in the local stack and in the image.
- Add the test setup for integration tests: a test database per pytest worker, migrated once, with each test rolled back.
- Add a check that the models and the migrations do not drift apart.
- Document the migration commands in the developer guide.

No API route, response or user-visible behavior changes.

## Capabilities

### New Capabilities

None. This change adds infrastructure only and sets `skip_specs: true`.

### Modified Capabilities

None.

## Impact

- **Code**: new `backend/src/atletico_hub/db/` (settings, engine, session, base model, migrations); `main.py` unchanged.
- **Dependencies**: `sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`.
- **Image and stack**: `docker-entrypoint.sh` runs `alembic upgrade head` before the command when asked to; `compose.yaml` turns it on for the `api` service.
- **Tests and CI**: integration tests reach Postgres through the `DB_*` variables, which `backend-tests` already sets. No workflow change expected.
- **Docs**: developer guide (migrations), `ARCHITECTURE.md` (database access), `CODE_GUIDELINES.md` (repository pattern on SQLAlchemy).
- **ADR**: takes a project-wide decision on database access and migrations, recorded as [ADR-0005](../../../../docs/documents/architecture/adr/0005-database-access-through-sqlalchemy-and-alembic.md) (accepted). It extends ADR-0002 and does not contradict it.
