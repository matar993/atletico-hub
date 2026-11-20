# Code guidelines

Principles, code patterns and testing rules for Atletico Hub. For how to propose, check and merge a change, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Principles

When two principles collide, pick the one that cuts future cost in this codebase.

**Hard rule: refactor to the principle first, then change behavior.**

1. **Separation of Concerns**: one kind of work per part (UI, domain, persistence, infra). Root principle.
2. **Encapsulation and information hiding**: small stable contract; hide internals.
3. **High cohesion, loose coupling**: what changes together lives together; independent parts talk narrowly.
4. **DRY**: one authoritative representation of each piece of knowledge, not of every similar line. Avoid over-DRY.
5. **KISS**: the simplest design that works. Complexity is the long-term tax.
6. **Single Responsibility**: one reason to change.
7. **Depend on abstractions**: policy does not depend on details; both depend on contracts.
8. **YAGNI**: no speculative features, frameworks or "later" hooks.
9. **Composition over inheritance**: assemble pieces; do not grow fragile hierarchies.
10. **Open/Closed, with discipline**: extend at stable boundaries, and only where change showed up twice.

Also worth following: Law of Demeter, fail fast, illegal states unrepresentable, optimize for deletion, do one thing and compose.

Treat these as constraints. Break a slogan when judgment says so.

## Code patterns

Backend (`backend/src/atletico_hub/`):

- Use Pydantic models and type hints. See the [`pydantic`](.agents/skills/pydantic/SKILL.md) skill for models with constraints or hierarchies.
- Build the API with FastAPI as the [`fastapi`](.agents/skills/fastapi/SKILL.md) skill describes: dependencies, response models, streaming responses.
- Split each feature into layers ([ADR-0006](docs/documents/architecture/adr/0006-layered-feature-packages-in-the-api.md)). A layer imports only the layers below it; `make lint-imports` checks it:
  - `router.py`: HTTP only. Parse input, call the service, return a schema, turn domain exceptions into HTTP errors. No business rule, no query.
  - `service.py`: business rules, one public method per use case. Never import FastAPI or raise `HTTPException`: raise a domain exception declared in the same module.
  - `schemas.py`: Pydantic request and response models. Never return an ORM model from a route.
  - `repository.py`: queries through the SQLAlchemy `Session` that `get_session` gives (`atletico_hub/db/session.py`). No business rule, no commit.
  - `models.py`: SQLAlchemy models, the entities. No separate domain model and no mapper.
- The service depends on `Protocol`s declared in `service.py`, never on a concrete repository (principle 7, depend on abstractions). The repository satisfies the `Protocol` structurally, so it imports nothing from the service.
- The service owns the transaction: it calls `commit()` once its use case is complete. `get_session` only closes the session. Repositories never commit.
- Wire the layers in the router with `Depends`. Construct dependencies in one place; never build them inside a service.
- Keep functions small: one level of abstraction per function. ruff fails above complexity 8, 5 arguments, 8 branches, 4 returns or 30 statements.
- Declare tables as SQLAlchemy models that extend `atletico_hub.db.base.Base`, in the `models.py` of their feature (`atletico_hub/<feature>/models.py`). Each model change ships with its Alembic migration ([setup guide](docs/documents/developer-guide/setup/README.md#database-migrations)).
- Write routes that use the database as plain `def` functions: database access is synchronous ([ADR-0005](docs/documents/architecture/adr/0005-database-access-through-sqlalchemy-and-alembic.md)).
- Use immutability for classes. No setter methods (illegal states unrepresentable).
- Return `Optional[Something]` when the result may be None (illegal states unrepresentable).
- Write no docstrings unless required: express intent through names (principle 5, KISS).
- Group code by meaning, not by kind. Never add a module that collects objects of one kind (`enums.py`, `constants.py`, `exceptions.py`, `types.py`, `utils.py`). Declare an enum, a constant or an exception in the module of the feature that uses it, next to the code that uses it. Move it to a shared module only when two features need it, and name that module for what it means (principles 1 and 3, separation of concerns and cohesion).
- Catch specific exceptions. Chain them with `from ex` (fail fast).
- Log with context before re-raising, with `exc_info=ex, stack_info=True`. Put the context in the exception message too.
- Enforce every access rule in the API. The web app hides what a user may not do, but never decides it.
- Personal data of players (phone numbers, birth dates, medical certificates) never goes to logs.

Web app (`frontend/src/`):

- Group code by feature (`src/<feature>/`), with its components, hooks and tests together. Routes in `src/routes/` stay thin: they import the page of their feature.
- Call the API only through `src/lib/api/client.ts`, typed by the generated `schema.d.ts`. Never write API types by hand.
- Keep server state in TanStack Query. Keep local state in the component that owns it.
- Design for a phone screen first: most users open the app from a phone.
- Use semantic HTML and accessible names: tests query by role and name, and ESLint checks accessibility (`jsx-a11y`).

Architectural boundaries: [ARCHITECTURE.md](ARCHITECTURE.md).

## Tests

Each new feature or bugfix has tests.

### Pyramid

Write many unit tests, some integration tests and few end-to-end tests. The lower the level, the faster and more precise the test.

| Level | Backend | Web app | Share |
|---|---|---|---|
| Unit | `tests/unit/` | Vitest | Most tests |
| Integration | `tests/integration/` | none | Some |
| End to end | `tests/system/` | Playwright | Few |

- A unit test never launches the stack. It uses mocks, so it runs in milliseconds.
- Test each backend layer at its own level:
  - service: unit tests, with in-memory fakes of its `Protocol`s. Prefer a fake to a `Mock`: it survives refactors. Most tests live here.
  - repository: integration tests on real Postgres, with the `db_session` fixture.
  - router: system tests through `TestClient`. One per route and outcome: status code, response shape, error mapping, data stored.
- Test business rules at the unit level. Use the higher levels only for what a unit test cannot show: real SQL, the wiring of the whole app, a flow in the browser.
- A bug fix starts with a test that fails for the bug, at the lowest level that can show it.

### Backend tests (`backend/tests/`)

- The three folders each mirror `atletico_hub/` and each contains an `__init__.py`:
  - `tests/unit/`: no database, network or app. Pure logic.
  - `tests/integration/`: a real Postgres, but not the whole app. Use the `db_session` fixture: each test's changes are rolled back.
  - `tests/system/`: the whole app, through FastAPI's `TestClient`.
- A test needing more than one level goes in the highest one. A test file never mixes levels: split it.
- One test file per class or module under test, named `test_<module>.py`.
- One test class per file, named `Test<ClassName>`.
- Name test methods `test_<method>_<behaviour>`.
- Build the test data inline in each test: no shared setup helpers or module-level fixtures.
- Call the method under test with keyword arguments.

### Web app tests (`frontend/`)

- Unit tests sit next to the code they test, named `<Component>.test.tsx`, and run in Vitest with Testing Library.
- Query elements by role and accessible name, not by class or test id.
- Browser tests live in `frontend/e2e/` and run on the production build with the image's security headers.

How to run the tests and the coverage floor: [Setup and development](docs/documents/developer-guide/setup/README.md#commands-and-checks).
