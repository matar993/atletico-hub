# Tasks

## 1. Dependencies and settings

- [x] 1.1 Add `pwdlib[argon2]` and `pydantic[email]` to `backend/pyproject.toml` and run `make lock`; verify `uv.lock` changes and the `api` image builds (`docker compose build api`)
- [x] 1.2 Add `AuthSettings` (prefix `AUTH_`, `cookie_secure: bool = True`) in `atletico_hub/auth/settings.py`, set `AUTH_COOKIE_SECURE=false` in `compose.yaml` and document it in `example.env`; verify with a unit test of the default and of the environment override

## 2. Squad model and data access

- [x] 2.1 Add `players/models.py` (`Player`) and `auth/models.py` (`Account` with `Role` as a non-native enum, `Session`, `Invite`), as in design D2, and one Alembic revision for the four tables; verify the migration integration test upgrades and downgrades cleanly
- [x] 2.2 Add `players/repository.py` (add, list sorted by last name then first name, with the account email by outer join) with integration tests on `db_session`; verify `make test` passes
- [x] 2.3 Add `auth/repository.py` (accounts by email and by player, sessions by token hash, invites by token hash, delete the open invites of a player, delete the sessions of an account) with integration tests on `db_session`; verify `make test` passes

## 3. Auth rules (services)

- [x] 3.1 Add the token helpers (generation, SHA-256) and the `PasswordHasher` adapter on `pwdlib`; verify with a unit test of the token hash and an integration test that the real hasher verifies its own hash and rejects another password
- [x] 3.2 Add `players/service.py` (add a player with trimmed names of 1 to 50 characters, list the squad) with unit tests on fakes; verify `make test` passes
- [x] 3.3 Add the login, session check, session extension and logout use cases to `auth/service.py`, with the `Clock` and `PasswordHasher` protocols, the dummy-hash verify for unknown emails and the lockout after 5 failures for 15 minutes; verify with unit tests on fakes that cover every scenario of the requirements "Login with email and password", "Login lockout", "Session" and "Logout"
- [x] 3.4 Add the invite use cases to `auth/service.py`: create (cancels earlier links, 7-day expiry), open, complete for a new account (role `player`, email in use leaves the link valid) and for a reset (new password, all sessions ended, lockout cleared); verify with unit tests on fakes that cover every scenario of `player-invites`

## 4. HTTP layer

- [x] 4.1 Add `tests/system/conftest.py` with a `TestClient` whose `get_session` is overridden by `db_session`; verify the existing `test_main.py` still passes with it
- [x] 4.2 Add `auth/dependencies.py` (`require_csrf_header`, `current_account` with cookie refresh, `require_admin`) and declare `require_csrf_header` app-wide in `main.py`; verify with system tests: POST without the header answers 403 and changes nothing, GET without it answers normally
- [x] 4.3 Add `auth/schemas.py` and `auth/router.py` with the `/auth` routes of design D8, and wire the router in `main.py`; verify with system tests per route and outcome, including the cookie flags (`HttpOnly`, `SameSite=Lax`, `Max-Age`) and the 401, 404, 409 and 429 mappings
- [x] 4.4 Add `players/schemas.py` and `players/router.py` (`GET /players`, `POST /players` for admins only, email only for admins) and wire it; verify with system tests for both roles and without a session
- [x] 4.5 Add the system test that walks `app.routes` and checks that every route outside the allowlist of design D7 answers 401 without a session; verify it passes, and fails when a test route without the dependency is added
- [x] 4.6 Run `make lint`, `make typecheck` and `make lint-imports`; verify all three pass with the new packages

## 5. First admin

- [x] 5.1 Add `atletico_hub/auth/cli.py` and the `make create-admin` target, as in design D9; verify with a unit test that it refuses an email in use, and by hand that the created admin logs in through `POST /auth/login`
- [x] 5.2 Document `make create-admin` and `AUTH_COOKIE_SECURE` in `docs/documents/developer-guide/setup/README.md`; verify the documented command runs as written

## 6. Web app: session and guard

- [x] 6.1 Regenerate `src/lib/api/schema.d.ts` (`make ui-gen-api`); verify `make ui-typecheck` passes
- [x] 6.2 Add the client middleware of design D11 (CSRF header on writes, 401 to login) with a unit test of each branch; verify `make ui-test` passes
- [x] 6.3 Move the section routes under `src/routes/_authenticated/` with a `beforeLoad` guard, render `AppLayout` there and the theme provider in `__root.tsx`, and pass the `QueryClient` in the router context; verify with unit tests that a 401 on the current user redirects to `/login` with the `redirect` search value and that the paths of the sections do not change
- [x] 6.4 Add the login page at `/login`, with the safe `redirect` rule of design D10; verify with unit tests: failed login shows the API message, success opens the requested section, an external `redirect` opens Home
- [x] 6.5 Show the user's name and a logout button in the header of `AppLayout`; verify with a unit test that logout calls the API and opens the login page

## 7. Web app: invite and Rosa

- [x] 7.1 Add the invite page at `/invite/$token` (new account form, reset form, "Link non valido o scaduto. Chiedi un nuovo link all'admin."); verify with unit tests for the three states and the submit of each form
- [x] 7.2 Replace the Rosa placeholder with the squad list, and for admins the "Aggiungi giocatore" dialog and the invite link with the copy button and the shown-once warning; verify with unit tests for the role `player` (no email, no action) and the role `admin`

## 8. Browser tests

- [x] 8.1 Add a shared `page.route` stub for `/api/auth/me` and use it in `e2e/navigation.spec.ts` and `e2e/theme.spec.ts`; verify `make ui-e2e` passes
- [x] 8.2 Add `e2e/auth.spec.ts`: a section without a session opens login and returns to it after login; logout opens login; verify `make ui-e2e` passes

## 9. Documentation

- [ ] 9.1 Add the user guide pages for login and for invite links (player and admin side) under `docs/documents/user-guide/` and list them in its index; update "Today" and the components table in `ARCHITECTURE.md`; verify every link resolves and `make validate` passes

## 10. Integration check

- [ ] 10.1 Run `make test`, `make lint`, `make typecheck`, `make lint-imports`, `make ui-checks`, `make ui-e2e` and `make validate` on the final tree; verify all pass, and walk the flow by hand on the stack: create the admin, add a player, create a link, register in a private window, log out, log in

## Workflow follow-up

- Archive the change with `/openspec-archive-change`; at archive, set ADR-0007 to "accepted" in the ADR and in its index.
