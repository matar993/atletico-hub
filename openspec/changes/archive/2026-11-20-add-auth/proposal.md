# Proposal

## Why

The app is open to anyone who reaches it, and it has no notion of who is using it. Every next feature (events, call-ups, roles and permissions) needs to know the user, and only members of the squad must get in. This change adds the identity: an account per player of the squad, a login, and a session.

## Changes

- Add a minimal squad: a player has a first name and a last name. An admin adds players and sees the list on the Rosa page. Full squad management (roles on the pitch, numbers, contacts) stays out.
- Add accounts: each account belongs to exactly one player and has an email, a password and a role, `admin` or `player`.
- Add personal invite links: an admin creates a link for one player and sends it, for example on WhatsApp. The link is single-use, expires after 7 days, and a new link cancels the previous one.
  - A player without an account opens the link, chooses email and password, and is signed in as that player.
  - A player with an account opens the link and chooses a new password; all their sessions end. This is how an admin resets a password.
- Add login with email and password, and logout. The email is unique and case-insensitive, and it is not verified: the invite link proves who the player is. The password has at least 8 characters, with no composition rule.
- After 5 failed logins on one account, login on it is refused for 15 minutes.
- Sessions live in the database, behind an httpOnly cookie. A session lasts 30 days and each use extends it.
- Every request that changes data must carry a custom header, as protection against cross-site request forgery.
- The whole web app requires login, except the login page and the invite page. Without a session the app opens the login page. The header shows the user's name and a logout button.
- Add a command, `make create-admin`, that creates the first admin: a player and an admin account.
- Out of scope: permissions and the RBAC check (a separate change), password change by the user, login with Google or magic link, email sending, deploy.

## Capabilities

### New Capabilities

- `user-auth`: accounts, login, logout, sessions, login lockout, protection against cross-site requests, first admin.
- `player-invites`: invite links that let a player of the squad create an account or set a new password.
- `squad`: the players of the squad, added by an admin and listed on the Rosa page.

### Modified Capabilities

- `app-shell`: every section requires login; the header shows the user and a logout button; Rosa is no longer a placeholder page.

## Impact

- Code: new feature packages `backend/src/atletico_hub/auth/` and `backend/src/atletico_hub/players/`, wired in `main.py`; a migration with the tables of players, accounts, sessions and invites; tests at all three levels.
- Web app: login and invite pages, a guard on every section route, user and logout in the header, the Rosa page with the list of players and the admin actions, the API client sending the CSRF header. The browser tests answer the API calls with stubs, because they run without the stack.
- API: new routes under `/auth` and `/players`. Regenerated `frontend/src/lib/api/schema.d.ts`.
- Dependencies: `pwdlib[argon2]` and the `email` extra of `pydantic` in `backend/pyproject.toml`.
- Configuration: a setting for the `Secure` flag of the session cookie, off in the local stack because it runs on plain HTTP.
- Docs: user guide pages for login and invites, the "Today" section of `ARCHITECTURE.md`, the setup guide for `make create-admin`.
- Project-wide decision: how users sign in. New ADR-0007, status "proposed". No accepted ADR is contradicted.
