# Design

## Context

See proposal.md for the motivation and the specs for the behavior. The API has no feature yet: only `GET /health` and the database layer (`atletico_hub/db/`), with no table. Features follow the layers of ADR-0006. The web app is a TanStack Router SPA whose routes are flat files under `src/routes/`, all rendered inside `AppLayout`; it reaches the API only on its own origin, under `/api` (ADR-0004), and nginx or Vite strips the prefix. The browser tests run on the production build with no API behind them.

The project-wide part of this change, how users sign in, is recorded in [ADR-0007](../../../docs/documents/architecture/adr/0007-email-and-password-login-with-personal-invite-links.md) (accepted). Every other decision stays here.

## Goals / Non-Goals

**Goals:**
- The API is closed by default: a new route needs a session unless it is added to an explicit list of open routes.
- Business rules of auth (lockout, expiry, link validity, reset) are unit tested without a database and without real argon2.

**Non-Goals:**
- Permissions and a `require_permission` check: the RBAC change. This change has only an "admin only" check.
- Clean-up of expired sessions and used invites.
- Rate limiting by IP address.

## Decisions

### D1. Two feature packages: `players` and `auth`

- `players`: the `Player` model and the squad use cases (add, list).
- `auth`: the `Account`, `Session` and `Invite` models, login, logout, sessions, invites, the first admin.

`auth.models` points to `players.models` with a foreign key. The squad list needs the email of each account, so `players.repository` reads `auth.models.Account` with an outer join. Imports go one way between the model modules, so there is no import cycle.
- Alternative: one `auth` package that owns players too. Rejected: the squad grows on its own (roles on the pitch, numbers) and is not about sign-in.

### D2. Tables

| Table | Columns |
|---|---|
| `players` | `id`, `first_name`, `last_name`, `created_at` |
| `accounts` | `id`, `player_id` (unique, FK), `email` (unique, lower case), `password_hash`, `role`, `failed_logins`, `locked_until` (nullable), `created_at` |
| `sessions` | `id`, `account_id` (FK, cascade on delete), `token_hash` (unique), `last_used_at`, `created_at` |
| `invites` | `id`, `player_id` (FK, cascade on delete), `token_hash` (unique), `expires_at`, `used_at` (nullable), `created_at` |

- All times are `timestamptz`, in UTC.
- `role` is a string with a check constraint (`native_enum=False`), not a Postgres enum. The RBAC change can then add a role with a plain migration, without `ALTER TYPE`.
- The service stores the email lower case after trimming, so a plain unique index is enough. Alternative: the `citext` extension. Rejected: one more extension for one column.
- The lockout state lives on the account, because the spec counts failures per account.

### D3. Tokens

Session and invite tokens come from `secrets.token_urlsafe(32)`. The database stores their SHA-256, and a lookup is by that hash. A token has 256 random bits, so a fast hash is enough: argon2 is for low-entropy passwords only. A leaked database dump gives no usable session or link.

### D4. Passwords

`pwdlib` with argon2, through `PasswordHash.recommended()`. The service depends on a `PasswordHasher` `Protocol` (`hash`, `verify`). Unit tests use a fake, so they stay fast; one integration test covers the real hasher. When the email has no account, login still runs `verify` on a fixed dummy hash, so the answer takes about the same time whether or not the email exists.

### D5. Time is injected

The service takes a `Clock` `Protocol` (`now() -> datetime`). Unit tests pass a fake clock to cover the lockout end, the session expiry after 30 days and the link expiry after 7 days, without waiting.

### D6. Session flow

- Login and invite completion create a session and set the cookie `atletico_session`: httpOnly, `SameSite=Lax`, `Path=/`, `Max-Age` 30 days, and `Secure` when the setting is on.
- The dependency `current_account` reads the cookie and looks up the hash. A session older than 30 days since `last_used_at` is an error (401). A valid session gets `last_used_at = now`, and the response sets the cookie again with a fresh `Max-Age`, so the browser keeps it as long as the server does.
- Logout deletes the session row and clears the cookie. A password reset deletes every session row of the account.
- Settings: `AuthSettings` (pydantic-settings, prefix `AUTH_`) with `cookie_secure: bool = True`. `compose.yaml` sets `AUTH_COOKIE_SECURE=false`, because the local stack runs on plain HTTP and Safari drops `Secure` cookies there. The default stays safe for any later deploy.
- Alternative: JWT. Rejected in ADR-0007.

### D7. Closed by default, and CSRF, as app-wide dependencies

- `main.py` declares `FastAPI(dependencies=[Depends(require_csrf_header)])`. The check answers 403 to POST, PUT, PATCH and DELETE requests without `X-Requested-With: atletico-hub`, before any route runs. The API sends no CORS headers, so a page on another origin cannot add the header: the browser blocks the preflight. `SameSite=Lax` alone leaves top-level form posts and same-site subdomains open.
- Each router that needs a session declares `dependencies=[Depends(current_account)]` on the `APIRouter`, or takes the account as a parameter. Admin routes use `require_admin`, which answers 403 for the role `player`.
- A system test walks `app.routes` and checks that every route outside an explicit allowlist (`/health`, `/auth/login`, the invite routes, the OpenAPI pages) answers 401 without a session. A route added later without the dependency fails this test.
- The dependencies live in `auth/dependencies.py`. That module is HTTP wiring, like a router, so it may import FastAPI; the import-linter contract forbids FastAPI only in service, schemas, repository and models. The `players` router imports it.

### D8. Routes

| Method and path | Who | Use |
|---|---|---|
| `POST /auth/login` | anyone | email and password; sets the cookie; answers the current user |
| `POST /auth/logout` | signed in | ends the session; 204 |
| `GET /auth/me` | signed in | first name, last name, email, role |
| `POST /auth/invites` | admin | body `player_id`; answers `path` (`/invite/<token>`) and `expires_at` |
| `GET /auth/invites/{token}` | anyone | player name, `has_account`, and the email if there is one; 404 if not valid |
| `POST /auth/invites/{token}/accept` | anyone | email (only without an account) and password; sets the cookie |
| `GET /players` | signed in | the squad; `email` only for an admin |
| `POST /players` | admin | first name and last name |

- The API answers the path of the link, not a full URL: it does not know the public origin. The web app adds `window.location.origin`.
- Domain errors become HTTP errors in the routers: wrong credentials 401, lockout 429, link not valid 404, email in use 409, not an admin 403.
- Request schemas validate the email with Pydantic `EmailStr`, which needs the `email` extra of Pydantic (`email-validator`), and the password length with `Field(min_length=8, max_length=128)`.

### D9. First admin from a command

`python -m atletico_hub.auth.cli`: it asks for first name, last name and email with `input`, and for the password with `getpass`. It then calls the same service use case as invite completion, with the role `admin`. `make create-admin` runs it with `docker compose exec api`. The CLI is an entry point, like a router, and holds no rule.
- Alternative: an environment variable with admin emails. Rejected: it still needs a password, and a first-start endpoint is a bypass.

### D10. Web app routing

- `__root.tsx` renders the theme provider and an `Outlet`, so the login and invite pages get the theme too.
- A pathless layout route `_authenticated.tsx` renders `AppLayout`. Its `beforeLoad` loads the current user through TanStack Query (`ensureQueryData`). On a 401 it throws `redirect({ to: '/login', search: { redirect } })`. The section routes move under `src/routes/_authenticated/`; their paths do not change.
- `/login` and `/invite/$token` sit next to it, outside the layout.
- The `redirect` search value is used only when it is an internal path: it starts with `/` and not with `//`. Otherwise login opens Home. This blocks an open redirect.
- The router gets the `QueryClient` through its context.

### D11. API client

An `openapi-fetch` middleware on the client in `src/lib/api/client.ts`:
- adds `X-Requested-With: atletico-hub` to every request with the method POST, PUT, PATCH or DELETE;
- on a 401 from any route except login and the invite routes, removes the current user from the query cache and sends the router to `/login`.

Pages never handle the header or the 401 themselves.

### D12. Rosa page

`SquadPage` lists the players with TanStack Query. When the current user is an admin it also shows:
- an "Aggiungi giocatore" dialog (Radix Dialog, already a dependency);
- per player, a "Crea link d'invito" button, then the full link, a copy button (`navigator.clipboard.writeText`) and the warning that the link is shown only once.

The page shows or hides these actions only for usability. The API decides (CODE_GUIDELINES: access rules live in the API).

### D13. Tests

- Unit (`tests/unit/auth/`, `tests/unit/players/`): the services with in-memory fakes of the repositories, the hasher and the clock. Most of the scenarios of the specs live here.
- Integration: the repositories on real Postgres (`db_session`), the migration, the real argon2 hasher.
- System: a `tests/system/conftest.py` gives a `TestClient` whose `get_session` is overridden with `db_session`. One test per route and outcome, the matrix of D7, the CSRF check, the cookie flags. Tests sign in through the real login route, with an account built inline in the test.
- Web unit: login page, invite page, the guard, the middleware, the Rosa page for both roles.
- Browser: the existing specs and a few new ones answer `/api/*` with `page.route` stubs, because Playwright runs without the API. New specs: a section without a session opens login and comes back after it; logout.

## Risks / Trade-offs

- Anyone who knows a player's email can lock that account for 15 minutes with 5 wrong passwords → accepted for a team of about 20. A reset link from the admin clears the lock.
- The 429 on a locked account tells that the email has an account → accepted: it appears only after 5 failures, and it saves the player from guessing why login fails.
- One write per authenticated request, to extend the session → negligible at this scale. It can be limited to once per hour if it ever matters.
- Expired sessions and used invites stay in the database → a few rows per player. Clean-up is left for later.
- Browser tests run against stubs, so they do not catch a mismatch between the web app and the real API → the generated client types and the API system tests cover the contract.
- An admin who forwards the wrong link gives another player's account away → each link names the player on the invite page, and the admin sees on Rosa who has an account.

## Migration Plan

One Alembic revision creates the four tables. The database has no table today, so there is no data to move. Rollback is the downgrade of that revision. After the upgrade, run `make create-admin` once.
