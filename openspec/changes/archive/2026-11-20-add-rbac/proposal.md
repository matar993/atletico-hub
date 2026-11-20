# Proposal

## Why

Admins and players may do different things, but today the API knows only one rule: a few routes check `role == admin`. Every next feature (squad, events, call-ups, results, and later democratic call-ups) adds actions that some users may take and others may not. This change sets the base that all of them build on: permissions instead of roles, a check on every route, and an answer that tells the web app what the user may do.

## What Changes

- Add a catalogue of permissions in code, named `resource:action` (for example `squad:create`), and a fixed mapping from each role, `admin` and `player`, to its permissions. Adding a permission or a role needs a deploy.
- Every API route checks a permission, never a role. A route that is open without a session, or open to every signed-in user, is declared as such. A test fails when a route declares neither.
- Add a minimal Profilo page: every user sees their name, email and role, and changes their own first name and last name. The API action always applies to the signed-in user's own player and takes no player id, so it needs no check of who owns the player. An admin changes the name of any player from Rosa.
- Errors come in a fixed order: 401 without a session, then 403 without the permission, then 422 for an invalid body. A user without the permission learns nothing about the body the route expects.
- Answers carry, on each resource and list they return, a flag per action the user may take on it now. A flag combines the permission of the role with the domain rules of that resource, for example no invite link for an admin account. The web app shows or hides an action from these flags, so it repeats neither the mapping of roles nor the domain rules. The API still checks both on every request and refuses every action the user may not take.
- **BREAKING**: `GET /players` answers an object with the permissions on the squad and the list of players, each with its own permissions, instead of a plain list. The web app is its only client and changes in the same change.
- Add a Users panel for admins: the list of accounts with their role, and a role change. The API refuses to demote the last admin.
- Add an `atletico-hub` command, installed with the API, that runs on any host where the API runs: `atletico-hub create-admin` (today's first-admin command), `atletico-hub promote` to turn an account into an admin and recover when no admin is left, `atletico-hub reset-password` to set a new password for any account. The `make` targets stay only as shortcuts for the local stack.
- An admin account gets a new password only through `atletico-hub reset-password`. The API refuses an invite link for a player whose account is admin, and promoting an account cancels its open invite links. An account demoted from admin to player can be reset through a link again: this hole is accepted for now.
- Every request body refuses fields the route does not expect (422), so no route can take a field such as `role` by mistake.
- The API serves `/docs`, `/redoc` and `/openapi.json` only when a setting turns them on. The setting is off by default and on in the local stack.
- Out of scope: checks on who owns a resource (no route of this change needs one), password change by the signed-in user (a later issue), loss of access for a deactivated player (#28), password reset by email (#35), roles stored in the database, more than one team.

## Capabilities

### New Capabilities

- `access-control`: the permission model, the check on every route, the order of errors, the permission flags in answers, and strict request bodies.
- `user-roles`: the list of accounts with their role, the role change by an admin, the protection of the last admin, and the commands that promote an account and reset a password.
- `player-profile`: the Profilo page and the change of one's own name.

### Modified Capabilities

- `user-auth`: the requirement "Admin-only actions" is replaced by the permission check of `access-control`; the API documentation pages are off unless a setting turns them on.
- `player-invites`: an admin cannot create an invite link for a player whose account is admin; promoting an account cancels its open links.
- `squad`: the squad list carries permission flags; an admin changes any player's name; the Rosa page shows actions from the flags.
- `app-shell`: a seventh section, Utenti, only in the menu of an admin; a user without the permission who opens it sees a "not authorized" page; Profilo is no longer a placeholder page.

## Impact

- Code: a permission module in the `auth` package, a `require` dependency in place of `require_admin`, a new `users` feature package (router, service, schemas, repository), a profile router in the `players` package, subcommands in `auth/cli.py` behind an `atletico-hub` console script in `backend/pyproject.toml`, a settings class for the API documentation in `main.py`; tests at all three levels, and a table test of route × role.
- API: **BREAKING** shape of `GET /players`; new `PATCH /players/{player_id}`, `PATCH /profile`, `GET /users`, `PUT /users/{account_id}/role`; `POST /auth/invites` answers 403 for an admin account; every request body answers 422 on an unknown field. Regenerated `frontend/src/lib/api/schema.d.ts`.
- Database: no new table and no migration. The role stays on the account.
- Web app: Rosa reads the flags, with an edit dialog for the name; the Profilo page; a Users page and its menu entry for admins; a "not authorized" page.
- Configuration: `API_DOCS_ENABLED`, off by default, on in `compose.yaml`. `make ui-gen-api` reads `/openapi.json` from the local stack, so it keeps working.
- Docs: user guide pages for the Users panel and the Profilo page, the setup guide for the `atletico-hub` command on the local stack and on a deployed host, the "Today" section of `ARCHITECTURE.md`.
- Project-wide decision: how the API authorizes requests. New ADR-0008, status "proposed". It narrows ADR-0007 on one point: an admin account no longer gets a new password through an invite link, only from the command line.
