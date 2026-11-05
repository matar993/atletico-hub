.PHONY: lock test lint typecheck lint-fix autoformat \
	ui-typecheck ui-lint ui-format ui-format-check ui-test ui-build ui-checks ui-e2e ui-gen-api \
	validate hooks up down logs ps

# ---- Backend ----

# Regenerates backend/uv.lock from pyproject.toml. Run it after changing dependencies. Needs uv.
lock:
	cd backend && uv lock

# Runs the backend tests (pytest) in a one-off `api` container, with the database from the stack.
TEST_WORKERS ?= 4
test:
	docker compose run --rm api pytest tests -n $(TEST_WORKERS) --cov --cov-report=term

# Lints the backend with ruff from the uv environment of `backend/`. Fails on any finding.
lint:
	cd backend && uv run ruff check src/atletico_hub tests

# Type checks the backend with ty from the uv environment of `backend/`. Fails on any diagnostic.
typecheck:
	cd backend && uv run ty check src/atletico_hub tests

# Lints and applies the safe fixes. Run `make autoformat` after it.
lint-fix:
	cd backend && uv run ruff check --fix src/atletico_hub tests

# Formats the backend with ruff, so the formatting is deterministic.
autoformat:
	cd backend && uv run ruff format src/atletico_hub tests

# ---- Web app ----
# The ui-* targets run in the `ui` container: the stack must be up (`make up`). Exception: ui-e2e.

# TypeScript type check (tsc).
ui-typecheck:
	docker compose exec ui npm run typecheck

# ESLint.
ui-lint:
	docker compose exec ui npm run lint

# Rewrites the web app files with Prettier.
ui-format:
	docker compose exec ui npm run format

# Checks the formatting with Prettier, without changing files.
ui-format-check:
	docker compose exec ui npm run format:check

# Unit tests (Vitest).
ui-test:
	docker compose exec ui npm test

# Production build into frontend/dist.
ui-build:
	docker compose exec ui npm run build

# Everything the workflow's ui-checks job runs.
ui-checks: ui-typecheck ui-lint ui-format-check ui-test ui-build

# Browser tests (Playwright). Need no stack, but Node 22 and a browser on the host.
ui-e2e:
	cd frontend && npm ci && npx playwright install chromium && npm run test:e2e

# Regenerates frontend/src/lib/api/schema.d.ts from the running API.
# Run it after changing a route and commit the result.
ui-gen-api:
	docker compose exec ui npm run gen:api

# ---- Specs ----

# Validates all OpenSpec specs and changes. Part of the definition of done.
validate:
	openspec validate --all --strict

# ---- Git hooks ----

# Installs the hooks of .githooks/: the pre-commit hook runs the checks of the areas a commit touches.
hooks:
	git config core.hooksPath .githooks

# ---- Stack ----

# Builds and starts the stack in the background, in development mode.
up:
	docker compose up -d --build

# Stops and removes the containers. The volumes (database, web app dependencies) are kept.
down:
	docker compose down

# Follows the logs of all services.
logs:
	docker compose logs -f

# Lists the services and their state.
ps:
	docker compose ps
