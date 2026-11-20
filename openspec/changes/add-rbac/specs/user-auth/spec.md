# Spec Delta

## MODIFIED Requirements

### Requirement: API closed without a session
Every API route SHALL answer 401 to a request without a valid session, except the health check, login, the invite routes, and the API documentation pages when they are on.

#### Scenario: Route closed to anonymous requests
- **WHEN** a request without a session asks for the list of players
- **THEN** the API answers 401

#### Scenario: Health check stays open
- **WHEN** a request without a session calls the health check
- **THEN** the API answers 200

## ADDED Requirements

### Requirement: API documentation off by default
The API SHALL serve its documentation pages and its OpenAPI schema (`/docs`, `/redoc`, `/openapi.json`) only when a setting turns them on. The setting SHALL be off when it is not set, and on in the local stack.

#### Scenario: Setting not set
- **WHEN** the API runs without the setting and a request asks for `/openapi.json`
- **THEN** the API answers 404

#### Scenario: Local stack
- **WHEN** the API runs in the local stack and a request asks for `/openapi.json`
- **THEN** the API answers the OpenAPI schema

## REMOVED Requirements

### Requirement: Admin-only actions
**Reason**: Routes check a permission, never a role. The requirement "Permission check on every route" of `access-control` covers this case and every later one.
**Migration**: None for users: a player still gets 403 on every admin action. Routes use the permission check in place of the admin-only check.
