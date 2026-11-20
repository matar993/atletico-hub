# Design

## Context

See proposal.md for why. The project-wide decision is in [ADR-0008](../../../docs/documents/architecture/adr/0008-permissions-in-code-checked-on-every-route.md) (proposed). This design covers how it lands in the code of today.

Current state:

- `auth/models.py` holds `Role` (`admin`, `player`) on `Account`. `current_account` in `auth/dependencies.py` loads the account through its session on every request, so the role is always fresh.
- `require_admin` guards `POST /players` and `POST /auth/invites`. `GET /players` passes `with_emails=account.role == Role.ADMIN` to the service.
- `tests/system/test_main.py` walks `app.routes` and checks that every route outside `OPEN_ROUTES` answers 401 without a session.
- The import contracts (`backend/pyproject.toml`) layer each feature package as router > service > schemas > repository > models, and forbid FastAPI outside routers. Modules with other names, such as `auth/permissions.py`, sit outside the layers.
- The web app decides admin actions with `user?.role === 'admin'` in `src/squad/SquadPage.tsx`.
- CI checks `schema.d.ts` against `app.openapi()` (`.github/workflows/ci.yml`), not against the `/openapi.json` route.

## Goals / Non-Goals

**Goals:**

- One function decides every permission, and the flags in answers come from it.
- A route cannot ship without a permission decision; the test suite enforces it.
- No migration: the role stays a column of `accounts`.

**Non-Goals:**

- Checks of who owns a resource. They come with the first route that needs one.
- Caching permissions. The mapping is a constant in memory.

## Decisions

### D1. Permission module in the `auth` package

`auth/permissions.py`, plain Python, no FastAPI:

- `Permission(StrEnum)` with the values of the spec `access-control`: `squad:view`, `squad:view_email`, `squad:create`, `players:update`, `profile:update`, `invites:create`, `users:view`, `users:change_role`.
- `ROLE_PERMISSIONS: Mapping[Role, frozenset[Permission]]`, the fixed mapping.
- `can(account, permission) -> bool`: true when the role of the account has the permission.

No check of who owns a resource: no route of this change acts on a resource that may belong to another user. The profile route acts on the signed-in user's own player and takes no id (D3). When a real case comes, `can` gains an optional argument and the existing calls stay as they are (ADR-0008).

It lives in `auth` because it depends on `Account` and `Role`. Alternative: a new `access` package. Rejected: it would import `auth.models` and be imported by `auth` itself, for one module.

### D2. Route gate: `require(permission)`

`auth/dependencies.py` gets `require(permission)`, a factory that returns a dependency. The dependency takes `current_account`, raises 403 when `can` is false, and returns the account, so the endpoint can pass it to the service. The returned callable carries the permission as an attribute, read by the coverage test (D9). `require_admin` is removed.

FastAPI resolves a route's dependencies before it validates the body, and an `HTTPException` raised in a dependency stops the request at once. So a user without the permission gets 403 before any 422, as the spec "Order of errors" asks. A system test pins this, so a FastAPI upgrade that changes it fails loudly.

Routes open to every signed-in user (`GET /auth/me`, `POST /auth/logout`) keep `current_account` and are listed as such in the coverage test.

### D3. Own profile without an id

`PATCH /profile` (`profile:update`), body `{ first_name, last_name }`, renames the player of the signed-in account and answers the current user. It lives in a second router of the `players` package and calls `PlayerService.rename(player_id, first_name, last_name)` with `account.player_id`. `PATCH /players/{player_id}` (`players:update`, admins) calls the same method with the id of the path. Order: 401, 403, 422 from the body schema, 404 for an unknown player (admin route only), 422 from the name rules.

The Profilo page reads its data from `GET /auth/me`, which already answers name, email and role, so no `GET /profile` is added.

Alternative: one route `PATCH /players/{player_id}` for everyone, with a check that a player edits only their own. Rejected: it needs a check of who owns the player on every call, and a route without an id cannot reach another player by mistake.

### D4. Permission flags in answers

- `GET /players` answers `Squad { permissions: SquadPermissions { create }, items: [SquadMember] }`. Each `SquadMember` gains `permissions: PlayerPermissions { update, create_invite }`.
- `create` = `can(actor, squad:create)`; `update` = `can(actor, players:update)`. `create_invite` = `can(actor, invites:create)` and the player's account, if any, is not `admin`. The second part repeats the rule of D6, so the flag never offers an action the API refuses.
- `email` stays in each member, `null` without `squad:view_email`.
- The service computes the flags (`PlayerService.list_squad(actor)` in place of `list_squad(with_emails)`), because they are permission decisions. The router only maps to schemas.
- `GET /users` answers `Accounts { items: [AccountSummary] }`, each with `permissions: { change_role }`. No collection flag: the page offers no create action. The object shape leaves room for one.

### D5. `users` feature package

`users/router.py`, `service.py`, `schemas.py`, `repository.py`, using the models of `auth` and `players`:

- `GET /users` (`users:view`): accounts with their player, sorted by last name and first name.
- `PUT /users/{account_id}/role` (`users:change_role`), body `{ "role": "admin" | "player" }`. A dedicated route: the role never sits in a general update body.
- `UserService.change_role(actor, account_id, role)`: 404 for an unknown account; same role is a no-op; promotion deletes the open invites of the player; demotion runs the last-admin check of D7.

The CLI uses the same service for `promote`, so promotion cancels links in one place.

Alternative: put these routes in `auth`. Rejected: `auth` is about identity and sessions, and its router is already the largest; account administration is its own feature.

### D6. No invite link for an admin account

`AuthService.create_invite` loads the account of the player; when its role is `admin` it raises `AdminAccountError`, mapped to 403 with "La password di un admin si reimposta solo da riga di comando". Promotion cancels open links (D5), so a link created before the promotion cannot reset an admin either. Opening or accepting a link does not check the role again: no open link of an admin can exist.

### D7. Last admin under concurrency

`change_role` runs, in its transaction, `SELECT id FROM accounts WHERE role = 'admin' FOR UPDATE` before deciding. When the target is admin, the new role is `player`, and the selected rows are only the target, it raises `LastAdminError` (409 "Serve almeno un admin").

With two concurrent demotions, the second `SELECT ... FOR UPDATE` waits for the first transaction. Under Postgres READ COMMITTED it then re-checks the `WHERE` on the locked rows, so it no longer sees the demoted account and refuses. An integration test runs the two demotions on two connections.

Alternatives: a database trigger or check that counts admins. Rejected: the rule and its message would live in SQL, outside the service and its unit tests. Serializable isolation: it works too, but needs a retry on serialization failure.

### D8. Commands on the API host

`auth/cli.py` becomes a command with three subcommands, through `argparse`: `create-admin` (today's behaviour), `promote`, `reset-password`. Each asks its inputs on the terminal, the password through `getpass`.

`backend/pyproject.toml` declares `[project.scripts] atletico-hub = "atletico_hub.auth.cli:main"`, so every image that installs the project has an `atletico-hub` command. On a deployed host: `docker exec -it <api-container> atletico-hub promote`. The runtime image already installs the project (`uv sync --no-editable`), so it gets the script with no Dockerfile change.

`make create-admin`, `make promote` and `make reset-password` stay as shortcuts for the local stack only: `docker compose exec api atletico-hub <subcommand>`.

Alternative: only `python -m atletico_hub.auth.cli`. Rejected: it works too, but the operator must know the module path.

- `promote` calls `UserService.change_role` with no acting account: the command runs with operator rights on the host, so it skips the permission check but not the link cancellation.
- `reset-password` calls a new `AuthService.reset_password(email, password)`, which reuses the private reset of the invite flow: new hash, sessions ended, lockout cleared.

### D9. Route coverage and role matrix

- The walk in `tests/system/test_main.py` moves from status codes to declarations: for each `APIRoute`, the test looks in `route.dependant` for a `require` dependency. A route without one must be in `OPEN_ROUTES` or `SIGNED_IN_ROUTES`. The existing 401 walk stays.
- A parametrized table test lists (method, path, anonymous, player, admin) expected statuses for every route, signing in through fixtures that create one account per role. A test fails when a route of the app has no row, so the table stays complete.

### D10. Strict request bodies

A base `RequestModel(BaseModel)` with `model_config = ConfigDict(extra="forbid")` in `atletico_hub/schemas.py`. Every request schema (`LoginRequest`, `CreateInviteRequest`, `AcceptInviteRequest`, `AddPlayerRequest`, and the new ones) inherits it. Answer schemas stay plain `BaseModel`.

### D11. API documentation setting

`atletico_hub/settings.py` holds `ApiSettings` (`env_prefix="API_"`, `docs_enabled: bool = False`). `main.py` gets `create_app(settings)` and keeps `app = create_app(ApiSettings())` for uvicorn. When off, `docs_url`, `redoc_url` and `openapi_url` are `None`. `compose.yaml` sets `API_DOCS_ENABLED: "true"`, so `make ui-gen-api` keeps reading `/openapi.json`. CI calls `app.openapi()`, which works with the routes off.

### D12. Web app

- Rosa: actions from the flags of `GET /players`. "Aggiungi giocatore" from `permissions.create`; per row, "Crea link" from `create_invite` and a new "Modifica nome" dialog from `update`. After a rename the page refetches the squad and, when the admin renamed themselves, the current user.
- Profilo: `src/profile/ProfilePage.tsx` replaces the placeholder. It shows name, email and role from the current user and a form for first and last name that calls `PATCH /profile`, then refetches the current user and the squad, so the header shows the new name.
- Utenti: a new route `src/routes/_authenticated/users.tsx` and a feature folder `src/users/`. The menu entry carries an `adminOnly` mark in `layout/navigation.ts`; `NavMenu` hides it unless `user.role === 'admin'`. This is the one place the web app reads the role for permissions (ADR-0008).
- The route renders a `NotAuthorizedPage` without calling the API when the role is not `admin`. A 403 from any call shows the same page, so a role change during the session lands on it too.
- Each account row offers a role select when `change_role` is true. A 409 shows the API message and keeps the old value.

## Risks / Trade-offs

- [FastAPI changes the order of dependency and body resolution] → a system test pins 403 before 422 on a write route.
- [`GET /players` changes shape] → the web app is the only client and changes in the same pull request; the CI check on `schema.d.ts` catches a stale client.
- [`extra="forbid"` refuses a field the web app sends today] → `make ui-e2e` and the frontend unit tests run against the regenerated schema; the generated types already forbid unknown fields in TypeScript.
- [A demoted admin can be reset through a link and their account taken by another admin] → accepted for now (ADR-0008, Risks).
- [The operator runs `promote` on the wrong email] → the command prints the name of the player it promoted; the role can be changed back from the Users page.

## Migration Plan

No database migration. The API and the web app ship together. The existing accounts keep their roles. Rollback is a revert of the pull request.
