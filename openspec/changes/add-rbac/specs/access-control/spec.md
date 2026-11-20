# Spec Delta

## Purpose

Decides which user may take which action in the API, from the permissions of their role, and tells the web app what the user may do.

## ADDED Requirements

### Requirement: Permissions of each role
Each action of the API SHALL be guarded by a named permission of form `resource:action`. Each role SHALL grant a fixed set of permissions. A user SHALL have exactly the permissions of their role.

#### Scenario: Admin permissions
- **WHEN** the API checks the permissions of an account with role `admin`
- **THEN** it grants `squad:view`, `squad:view_email`, `squad:create`, `players:update`, `profile:update`, `invites:create`, `users:view` and `users:change_role`

#### Scenario: Player permissions
- **WHEN** the API checks the permissions of an account with role `player`
- **THEN** it grants only `squad:view` and `profile:update`

### Requirement: Permission check on every route
Every API route SHALL check a permission before it runs, except routes declared open without a session (health check, login, invite routes, API documentation) and routes declared open to every signed-in user (current user, logout). A user without the permission SHALL get 403 and the API SHALL change nothing.

#### Scenario: Player calls an admin route
- **WHEN** a user with role `player` asks to add a player to the squad
- **THEN** the API answers 403 and adds no player

#### Scenario: Route without a declaration
- **WHEN** a developer adds a route that checks no permission and is not declared open
- **THEN** the test suite fails and names the route

### Requirement: Order of errors
The API SHALL check, in this order: the session (401), the permission (403), the request body against its schema (422). A user without the permission SHALL get 403 even when the body does not match the schema. A body that is not valid JSON gets 422 before any of these checks.

#### Scenario: Player sends an invalid body to an admin route
- **WHEN** a user with role `player` sends a body without `last_name` to add a player
- **THEN** the API answers 403, not 422

#### Scenario: Anonymous request to an admin route
- **WHEN** a request without a session asks to add a player
- **THEN** the API answers 401

### Requirement: Permission flags in answers
An answer that returns a resource or a list SHALL carry, for the signed-in user, a `permissions` object with one boolean per action the web app can offer on it. Each flag SHALL equal the answer of the check the API runs on that action.

#### Scenario: Flags of a player
- **WHEN** a user with role `player` reads the squad
- **THEN** the flags to add a player, to change a player's name and to create an invite link are all false, and the API refuses each of those actions with 403

#### Scenario: Flags of an admin
- **WHEN** an admin reads the squad
- **THEN** the flags to add a player and to change a player's name are true, and the API accepts those actions

### Requirement: Role read on every request
The API SHALL read the role of the account on every request. A role change SHALL apply from the next request of that account, without ending its sessions.

#### Scenario: Demoted admin
- **WHEN** an admin is demoted to player and then, in the same session, asks to add a player
- **THEN** the API answers 403

### Requirement: Strict request bodies
Every request body SHALL accept only the fields its route declares. A body with any other field SHALL get 422, and the API SHALL change nothing.

#### Scenario: Unknown field in a body
- **WHEN** a user changes their own name and the body also carries `"role": "admin"`
- **THEN** the API answers 422 and changes neither the name nor the role
