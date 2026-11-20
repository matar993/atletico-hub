# ADR-0006: Each API feature is a package of layers: router, service, schemas, repository, models

**Date**: 2026-11-20
**Status**: accepted
**Deciders**: Marco Scalzo

## Context

The API has no feature yet, and coding agents write most of its code. Without a fixed shape, HTTP handling, business rules and queries end up in the same function, and the rules cannot be tested without a database. ADR-0005 already sends database access through repositories, but it does not say where business rules live, who commits a transaction, or how the rules are enforced.

## Decision

Each feature is a package `atletico_hub/<feature>/` with up to five layers. A layer imports only the layers below it:

| Module | Holds | Never |
|---|---|---|
| `router.py` | HTTP: input, output, status codes, wiring with `Depends`, domain errors turned into HTTP errors | business rules, queries |
| `service.py` | Business rules and use cases; domain exceptions; the `Protocol`s it needs; the transaction commit | FastAPI, HTTP errors, queries |
| `schemas.py` | Pydantic request and response models | ORM models used as API shapes |
| `repository.py` | Queries through the SQLAlchemy `Session` | business rules, commit |
| `models.py` | SQLAlchemy models: the entities | imports of other layers |

The service depends on `Protocol`s declared in `service.py`, not on concrete classes. The repository and the `Session` satisfy them structurally. The service commits at the end of each use case; `get_session` only closes the session. The SQLAlchemy models are the entities: there is no separate domain model. `import-linter` checks the layer order and keeps FastAPI out of every layer but the router, locally and in CI.

## Alternatives Considered

### Alternative 1: Full clean architecture (domain entities, ports, adapters, mappers)
- **Pros**: domain free of SQLAlchemy; storage swappable
- **Cons**: a mapper and a duplicate class per entity; more code to write and test
- **Why not**: a small app on one database; the cost buys nothing here (KISS, YAGNI)

### Alternative 2: Routes call repositories, no service layer
- **Pros**: fewer files
- **Cons**: business rules mix with HTTP; unit tests need the HTTP layer
- **Why not**: rules must be testable alone, in milliseconds

### Alternative 3: `get_session` commits at the end of each request
- **Pros**: less code in services
- **Cons**: the transaction boundary is hidden; a service cannot commit twice or decide when
- **Why not**: the use case is the right transaction boundary, and it must be visible

## Consequences

### Positive
- Business rules are unit tested with in-memory fakes of the `Protocol`s, without a database
- Each layer has one reason to change; a reader knows where to look
- Layer breaches fail `make lint-imports` and CI instead of review

### Negative
- Up to five files per feature, even for a small one
- Services call `commit()` by hand

### Risks
- A service forgets to commit, and the change is lost. Mitigation: a system test per write route checks the data is stored.
