# ADR-0008: Routes check permissions mapped from roles in code; answers carry the actions the user may take on each resource

**Date**: 2026-11-20
**Status**: accepted
**Deciders**: Marco Scalzo

## Context

The app has two roles, `admin` and `player`, and about 20 users in one team. Until now a few routes checked `role == admin`. Every next feature (squad, events, call-ups, results, and later democratic call-ups where every player votes) adds actions that only some users may take. More roles may come, for example a captain who manages call-ups. The web app must know which actions to offer, but the API stays the only place that enforces them.

## Decision

- Each action is guarded by a named permission of the form `resource:action`, fine-grained. A static mapping in code gives each role its set of permissions. Adding a permission or a role needs a deploy.
- Routes check a permission, never a role, through one function `can(account, permission)`.
- An action on the user's own data goes through a route without an id that always acts on the signed-in user, such as `PATCH /profile`. So no check of who owns a resource is needed today. When a route must act on a resource that may belong to another user, `can` gains an optional argument for it.
- Every route declares a permission, or is declared open without a session, or open to every signed-in user. A test fails on a route that declares none.
- Domain rules that make an action impossible on some resources, whoever asks (for example no invite link for an admin account, at least one admin left), live in the services, which refuse the action.
- Answers carry, for the signed-in user, a `permissions` object on each resource and list they return: one flag per action, true only when `can` allows it and no domain rule forbids it on that resource. The web app shows actions from these flags, so it repeats neither the mapping nor the domain rules. It reads the role only to show the role and the menu entry of the Users section.
- An admin account gets a new password only from the command line, never through an invite link.

## Alternatives Considered

### Alternative 1: Check the role in each route
- **Pros**: no code to add; the two roles exist already
- **Cons**: `role == admin` spreads across routes and services; a new role means finding and changing every check; no single list of who may do what
- **Why not**: it does not survive the first new role, and the test matrix has nothing to enumerate

### Alternative 2: Roles and permissions in the database, editable by an admin
- **Pros**: a new role, or a permission moved between roles, needs no deploy
- **Cons**: the catalogue of permissions stays in code anyway, because routes reference it, so code and rows must be kept in sync by migrations; needs a UI to edit roles, and system roles that cannot lose `users:change_role`; one more query or a cache per request
- **Why not**: a new permission always comes with new code that needs a deploy anyway, and new roles are rare. Because routes only call `can`, the mapping can move to the database later without changing routes or tests

### Alternative 3: An external policy engine (Casbin, OPA, Oso, a relationship-based model)
- **Pros**: expressive policies, audit tools, policies outside the code
- **Cons**: a new dependency and a policy language to learn, for two roles and a fixed mapping
- **Why not**: the rules fit in one module of plain code

### Alternative 4: The list of the user's permissions in the current-user answer
- **Pros**: one call gives the web app every permission
- **Cons**: it mixes identity with authorization; a global list cannot say what the user may do on one resource and not on another, which a flag on the resource can (for example no invite link on an admin account)
- **Why not**: flags on each resource stay next to what they describe and also carry the domain rules of that resource

## Consequences

### Positive
- One place lists what each role may do; the route × role test matrix follows from it
- A route cannot ship without a decision on who may call it
- New roles plug into the mapping without changes to routes or to the web app
- The web app never duplicates the mapping, so its buttons cannot drift from what the API allows

### Negative
- Each flag must apply the same domain rules as the service, so a rule added to a service must also reach its flag
- Every answer that returns a resource carries a `permissions` object, and list answers become objects instead of plain arrays
- A permission or role change needs a deploy
- The web app still reads the role for the menu entry of the Users section, a small duplication of the mapping

### Risks
- A future route takes the id of a resource that belongs to one user and checks only the role. Mitigation: prefer routes without an id for one's own data; the route × role table test lists every route, so a new one gets reviewed.
- ADR-0007 says an invite link sets a new password for any player with an account. This ADR narrows it: not for an account with role `admin`. An admin demoted to player can be reset through a link again; this is accepted while the team is small.
