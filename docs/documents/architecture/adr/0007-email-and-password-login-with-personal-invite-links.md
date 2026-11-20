# ADR-0007: Users sign in with email and password; accounts come only from personal invite links; sessions live in Postgres

**Date**: 2026-11-20
**Status**: proposed
**Deciders**: Marco Scalzo

## Context

The app serves one team of about 20 players, and only players of the squad may get in. It runs on localhost for now, with no deploy, no domain and no email provider. The link to the app travels on WhatsApp, which opens it in its in-app browser. Every later feature, and the roles of the RBAC change, need to know who the user is.

## Decision

- A user signs in with an email and a password. The password is stored as an argon2 hash.
- An account is created only through a personal, single-use invite link that an admin creates for one player of the squad. There is no open registration. The same link, for a player who already has an account, sets a new password: it is the only password reset.
- A session is a random token in an httpOnly, `SameSite=Lax` cookie. Postgres stores only the hash of the token, so a session can be revoked.
- Every write request carries the header `X-Requested-With: atletico-hub`, as protection against cross-site request forgery.

## Alternatives Considered

### Alternative 1: Google login (OpenID Connect)
- **Pros**: no password to store; no reset flow
- **Cons**: a Google Cloud project and registered redirect URIs; Google blocks its sign-in in the WhatsApp in-app browser; the login cannot run in browser tests
- **Why not**: more setup and harder tests for a team that only needs a gate. It can be added later, linked to the same account.

### Alternative 2: Magic link by email
- **Pros**: no password
- **Cons**: needs an email provider, DNS records for delivery and a mail catcher in the local stack; the link opened from WhatsApp signs in the in-app browser, not the real one
- **Why not**: the app sends no email today, and this is the most work of all options

### Alternative 3: Open registration, matched to the squad by email
- **Pros**: no link to send
- **Cons**: without email verification, anyone who knows a teammate's email can take their account
- **Why not**: unsafe without email sending; the invite link proves who the player is

### Alternative 4: JWT in browser storage
- **Pros**: no session table
- **Cons**: readable by any script on the page (XSS); cannot be revoked before it expires, so a password reset or a removed player keeps access
- **Why not**: the web app and the API share one origin (ADR-0004), so a cookie works without CORS, and revocation matters more than a saved query

## Consequences

### Positive
- No external service: the whole flow runs and is tested on the local stack
- One mechanism covers who may get in, the link between account and player, and password reset
- Sessions end at once on logout, on password reset, or when a player leaves

### Negative
- The API owns password security: hashing, login lockout, the length rule
- The admin must create and send a link for each player and for each forgotten password
- One database query per request to check the session

### Risks
- A forwarded invite link lets someone else take the account. Mitigation: the link works once, expires after 7 days, and a new link cancels the old one; the admin sees in Rosa which players have an account.
- The session cookie is not `Secure` while the app runs on plain HTTP. Mitigation: a setting turns the flag on; it must be on in any deploy over HTTPS.
