# Design

## Context

See proposal.md for the motivation. Today the backend is `atletico_hub.main:app` with `GET /health` only. The stack already passes `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` and `DB_DATABASE` to the `api` container and to the `backend-tests` CI job, and `docker-entrypoint.sh` waits for Postgres when `WAIT_FOR_DB=true`. The image copies only `src/`, so anything the API needs at runtime, migrations included, lives in the package. Tests run with `pytest -n 4` (xdist), so several workers hit Postgres at once.

The project-wide choice of library is recorded in [ADR-0005](../../../../docs/documents/architecture/adr/0005-database-access-through-sqlalchemy-and-alembic.md).

## Goals / Non-Goals

**Goals:**
- One way to open a session, used by routes through a dependency and by tests.
- Migrations that run the same way in the local stack, CI and the image.
- Integration tests that are isolated and safe under xdist.

**Non-Goals:**
- No tables. The first table arrives with `add-auth-and-roles`.
- No database check in `GET /health`. It keeps its current contract.
- No async database access.
- No connection-pool tuning beyond SQLAlchemy defaults.

## Decisions

### Synchronous SQLAlchemy with psycopg 3
Routes that use the database are plain `def` functions; FastAPI runs them in its thread pool.
- Alternative: async SQLAlchemy with `asyncpg`. Rejected: async sessions add lazy-loading pitfalls and test complexity, and a team app with a handful of users gains nothing from it.

### Settings with `pydantic-settings`
A `DatabaseSettings` model reads the existing `DB_*` variables and builds the URL (`postgresql+psycopg://…`). No new variable names, so compose and CI stay as they are.
- Alternative: one `DATABASE_URL` variable. Rejected: it would change compose, CI and `example.env` for no gain.

### Module layout: `atletico_hub/db/`
`settings.py` (`DatabaseSettings`), `engine.py` (engine and session factory from settings, built on first use), `session.py` (the `get_session` dependency, one session per request, closed after it), `base.py` (the declarative `Base` that every feature's models extend), `migrations/` (Alembic `env.py` and `versions/`). Feature models live with their feature, for example `atletico_hub/auth/models.py`, per CODE_GUIDELINES "group by meaning". Repositories wrap the session per feature, so unit tests mock the repository, not SQLAlchemy.
- Alternative: one `models.py` for all tables. Rejected: CODE_GUIDELINES forbids modules that collect one kind of object.

### Alembic configured in code, inside the package
`alembic.ini` sits in `backend/` for the CLI and points `script_location` at `atletico_hub.db:migrations`; `env.py` takes the URL from `DatabaseSettings`, never from the ini file, or the connection the integration tests pass. A post-write hook runs ruff on each new revision. Autogenerate reads `Base.metadata`, so `env.py` imports every feature's models module.

### Migrations run before the API starts
`docker-entrypoint.sh` runs `alembic upgrade head` when `MIGRATE_DB=true`, after the existing wait for Postgres. `compose.yaml` sets it for `api`. The production image gets the same switch.
- Alternative: run migrations in the FastAPI startup hook. Rejected: a failing migration should stop the container before it serves traffic.
- Several API replicas that start together would each run the migrations, in the entrypoint as in a startup hook: one fails on the concurrent DDL and restarts. One replica runs today. More replicas need a `pg_advisory_lock` in `env.py` or a one-off migration job.
- Alternative: a manual `make migrate` step. Rejected: easy to forget after pulling `develop`.

### Integration test database
A session-scoped pytest fixture in `tests/integration/conftest.py` creates `<DB_DATABASE>_test_<run id>_<worker id>`, runs `alembic upgrade head` on it once, and drops it at the end. A per-test fixture opens a connection, begins a transaction, binds a session to it with `join_transaction_mode="create_savepoint"`, and rolls back after the test. Tests never see each other's rows, and neither the workers nor two runs on the shared stack share a database.
- This is test infrastructure, not test data: CODE_GUIDELINES' "no shared setup helpers" still applies to rows, which each test builds inline.
- Alternative: one shared test database with table truncation. Rejected: unsafe under xdist.

### Drift check
An integration test runs `alembic check` against the migrated test database and fails on any difference between `Base.metadata` and the schema, so a model change without a migration fails CI. `alembic check` goes through `env.py`, so it sees the same models as autogenerate.

## Risks / Trade-offs

- [Python 3.14 and new SQLAlchemy/psycopg wheels] → uv lock pins them; `make test` and the image build run in CI.
- [A bad migration blocks API start] → intended: the container fails fast; `alembic downgrade -1` rolls back locally.
- [Forgetting to import a new models module in `env.py`] → autogenerate misses its table. The drift check catches it only when the test run imports the module elsewhere, which the feature's own tests do. The setup guide names the import as a step.
- [Test databases leak if a run is killed, since names never repeat] → the setup guide gives a command that drops every `<DB_DATABASE>_test_*` database.

## Migration Plan

Existing local databases are empty, so the first `make up` after merge only creates Alembic's `alembic_version` table. Rollback: revert the pull request; the extra table is harmless.
