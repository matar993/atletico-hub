# ADR-0002: The backend is a Python FastAPI app on Postgres

**Date**: 2026-11-05
**Status**: accepted
**Deciders**: Marco Scalzo

## Context

The app needs an HTTP API for the web app and a relational store for players, matches and the team's data. The team already works with Python, FastAPI, uv and Postgres, and the agent skills of this repository (`fastapi`, `pydantic`) and its checks are written for that stack.

## Decision

The backend is a Python 3.14 app on FastAPI, with Pydantic models, managed with uv (`backend/uv.lock` is the only lock). Data lives in Postgres. Lint and format run with ruff, type checks with ty, tests with pytest, with a coverage floor of 90%.

## Alternatives Considered

### Alternative 1: Node.js backend (NestJS or Fastify) in TypeScript
- **Pros**: one language across backend and web app
- **Cons**: the team's experience, skills and checks are on the Python stack
- **Why not**: the shared language is worth less than reusing what the team knows and has automated

### Alternative 2: Backend-as-a-service (Supabase, Firebase)
- **Pros**: authentication, storage and database without code to run
- **Cons**: business rules split between client and platform rules, vendor lock-in, harder to test locally
- **Why not**: the team wants its rules in tested code that runs the same in the local stack and in production

## Consequences

### Positive
- The agent skills and the checks of this repository apply as they are
- FastAPI publishes an OpenAPI document, from which the web app generates its client

### Negative
- Two languages in the repository: Python and TypeScript

### Risks
- Python 3.14 is recent: a dependency may lag behind. Mitigation: uv pins the interpreter, and the lock is checked in CI
