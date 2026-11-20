# Tasks

## 1. Permission model

- [x] 1.1 Add `auth/permissions.py` as in design D1 (`Permission`, `ROLE_PERMISSIONS`, `can`); verify unit tests cover the set of each role
- [x] 1.2 Add `require(permission)` to `auth/dependencies.py` (design D2), move `POST /players` to `squad:create`, `POST /auth/invites` to `invites:create`, `GET /players` to `squad:view`, and remove `require_admin`; verify the existing system tests pass and a new one shows a player sending an invalid body to `POST /players` gets 403, not 422
- [x] 1.3 Rewrite the route walk in `tests/system/test_main.py` as in design D9 (`OPEN_ROUTES`, `SIGNED_IN_ROUTES`, `require` declaration) and add the route × role table test with one account per role; verify both pass, and fail on a route mounted without a declaration or without a table row
- [x] 1.4 Run `make lint`, `make typecheck` and `make lint-imports`; verify all three pass

## 2. Strict bodies and API documentation

- [x] 2.1 Add `RequestModel` with `extra="forbid"` in `atletico_hub/schemas.py` and make every request schema inherit it (design D10); verify system tests show 422 for an unknown field on login, add player, create invite and accept invite, with nothing changed
- [x] 2.2 Add `ApiSettings` and `create_app(settings)` (design D11), set `API_DOCS_ENABLED` in `compose.yaml` and `example.env`; verify system tests show `/openapi.json`, `/docs` and `/redoc` answer 404 by default and answer with the setting on, and that `app.openapi()` still returns the schema
- [x] 2.3 Document `API_DOCS_ENABLED` in `docs/documents/developer-guide/setup/README.md`; verify `make ui-gen-api` runs as written on the stack

## 3. Squad and profile: flags and name change

- [x] 3.1 Change `PlayerService.list_squad` to take the acting account and return the flags of design D4; verify unit tests on fakes for player and admin, including `create_invite` false on an admin account
- [x] 3.2 Add `PlayerService.rename(player_id, first_name, last_name)` (design D3); verify unit tests cover a valid rename, an unknown player and invalid names
- [x] 3.3 Change `GET /players` to the `Squad` shape and add `PATCH /players/{player_id}` (`players:update`), with rows in the role matrix; verify system tests for each scenario of the `squad` delta spec
- [x] 3.4 Add `PATCH /profile` (`profile:update`) in a profile router of the `players` package, wired in `create_app`, with rows in the role matrix; verify system tests for each API scenario of the `player-profile` delta spec, including 422 on a body with `role`
- [x] 3.5 Regenerate `frontend/src/lib/api/schema.d.ts` (`make ui-gen-api`); verify `make ui-typecheck` shows the places the new shape breaks

## 4. Invites: no link for an admin

- [x] 4.1 Refuse invite creation for an admin account in `AuthService.create_invite` and map it to 403 (design D6); verify unit and system tests for an admin target, the user's own admin account and a former admin

## 5. Users and roles (API)

- [x] 5.1 Add `users/repository.py` (accounts with player sorted, account by id, lock of admin rows, delete open invites of a player); verify integration tests on `db_session`
- [x] 5.2 Add `users/service.py` with `list_accounts(actor)` and `change_role(actor, account_id, role)` (design D5, D7); verify unit tests on fakes for promotion, self-demotion, last admin, unknown account, no-op and link cancellation
- [x] 5.3 Add an integration test that runs two demotions of the last two admins on two connections; verify one succeeds, the other raises the last-admin error, and one admin is left
- [x] 5.4 Add `users/schemas.py` and `users/router.py` (`GET /users`, `PUT /users/{account_id}/role`), wire it in `create_app`, add rows to the role matrix; verify system tests for every API scenario of the `user-roles` delta spec, including a demoted admin getting 403 in the same session
- [x] 5.5 Run `make lint`, `make typecheck` and `make lint-imports`; verify all three pass with the new package

## 6. Commands on the API host

- [x] 6.1 Turn `auth/cli.py` into the `create-admin`, `promote` and `reset-password` subcommands and add `AuthService.reset_password` (design D8); verify unit or integration tests for each subcommand, including unknown email and short password
- [x] 6.2 Declare the `atletico-hub` console script in `backend/pyproject.toml`, run `make lock`, and point `make create-admin`, `make promote` and `make reset-password` at it; verify `docker compose exec api atletico-hub --help` lists the three subcommands and the `runtime` image runs `atletico-hub --help`
- [x] 6.3 Document the command in `docs/documents/developer-guide/setup/README.md`, for the local stack (`make` targets) and for a deployed host (`docker exec -it <api-container> atletico-hub ...`); verify each runs as written on the stack: promote a player, reset an admin password, log in with it

## 7. Web app: Rosa

- [x] 7.1 Make Rosa read the flags of `GET /players` in place of `role` (design D12); verify unit tests for player and admin views, including no invite button on an admin's row
- [x] 7.2 Add the "Modifica nome" dialog on rows with `update`, refreshing the squad and the current user after a save; verify unit tests for save and API error
- [x] 7.3 Replace the Profilo placeholder with `src/profile/ProfilePage.tsx` (design D12): name, email and role from the current user, and a form that calls `PATCH /profile`; verify unit tests for save, the header name after save, and the API message on an empty name

## 8. Web app: Utenti and not authorized

- [x] 8.1 Add `adminOnly` to the Utenti entry in `layout/navigation.ts` and hide it in `NavMenu` for non-admins; verify unit tests for both roles
- [x] 8.2 Add `NotAuthorizedPage` and show it for a non-admin on `/users`, and on a 403 from any call; verify unit tests that the page makes no API call for a player
- [x] 8.3 Add the Utenti page in `src/users/` with the role select and the 409 message; verify unit tests for the list, a role change and the last-admin refusal
- [x] 8.4 Add `e2e/users.spec.ts` with stubbed API answers: an admin changes a role, a player opening `/users` sees the not authorized page; verify `make ui-e2e` passes

## 9. Documentation

- [x] 9.1 Add user guide pages for the Utenti panel and the Profilo page, list them in the user guide index, update the invite page for admin accounts, and update the "Today" section of `ARCHITECTURE.md`; verify links resolve and `make validate` passes

## 10. Integration check

- [ ] 10.1 Run `make test`, `make lint`, `make typecheck`, `make lint-imports`, `make ui-checks`, `make ui-e2e` and `make validate` on the final tree; verify all pass, then walk the flow by hand on the stack: promote a player from Utenti, try to demote the last admin, rename oneself on Profilo as a player, rename a player from Rosa as an admin, open `/users` as a player, reset an admin with `make reset-password`

## Workflow follow-up

- Open an issue for password change by the signed-in user, when the user asks.
- On archive, set ADR-0008 to "accepted" and update the ADR index.
