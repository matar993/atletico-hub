# Tasks

## 1. Dependencies and settings

- [x] 1.1 Add `sqlalchemy`, `psycopg[binary]`, `alembic` and `pydantic-settings` to `backend/pyproject.toml`, run `make lock` and `docker compose build api`; verify `docker compose run --rm api python -c "import sqlalchemy, psycopg, alembic"` succeeds
- [x] 1.2 Add `DatabaseSettings` reading the `DB_*` variables and building the psycopg URL; verify with unit tests in `tests/unit/db/` for the URL and for a missing variable

## 2. Engine and session

- [ ] 2.1 Add `atletico_hub/db/base.py`, `engine.py` and `session.py` (`get_session` dependency, one session per request, always closed); verify with a unit test that the session is closed after the dependency ends, also when the route raises

## 3. Migrations

- [ ] 3.1 Add `backend/alembic.ini` and `atletico_hub/db/migrations/` (`env.py` reading `DatabaseSettings` and `Base.metadata`, empty `versions/`); verify `docker compose run --rm api alembic upgrade head` creates `alembic_version`
- [ ] 3.2 Run `alembic upgrade head` in `docker-entrypoint.sh` when `MIGRATE_DB=true`, and set it for `api` in `compose.yaml`; verify `make up` starts the API and `docker compose logs api` shows the upgrade

## 4. Integration test setup

- [ ] 4.1 Add `tests/integration/conftest.py` with the per-worker test database and the per-test rolled-back session; verify with `tests/integration/db/test_session.py`, where a row written in one test is absent in the next, under `make test` (4 workers)
- [ ] 4.2 Add the drift check in `tests/integration/db/test_migrations.py`; verify it passes, and fails when a throwaway model without a migration is added locally
- [ ] 4.3 Verify `make test` passes with coverage at or above 90%

## 5. Documentation

- [ ] 5.1 Document migrations (create with `alembic revision --autogenerate`, apply, roll back, reset) in the developer guide, `MIGRATE_DB` in the stack notes, the database access in `ARCHITECTURE.md`, and the repository-on-SQLAlchemy pattern in `CODE_GUIDELINES.md`; verify each documented command runs as written

## Workflow follow-up

- Set ADR-0005 to "accepted" and update the ADR index at archive.
- Archive the change with `/openspec-archive-change` in the implementation pull request.
