# Users

The Utenti page (`/users`) lists every account of the app and lets an admin change its role. A user with the role `player` does not see Utenti in the menu. When a player opens `/users` by its path, the app shows a page that says "Non hai i permessi per vedere questa pagina", with a link to Home.

## Roles

| Role | What the user can do |
|---|---|
| `admin` | Everything a player can do, plus: add and rename players, see emails, create invite links, change roles |
| `player` | See the squad without emails, change their own name on the [Profilo page](profile.md) |

The role is changed only on Utenti or with the `promote` command on the API host.

## List the accounts

The page lists every account with first name, last name, email and role, sorted by last name and then first name. A player without an account is not listed: it has no role.

## Change a role

Choose the new role in the menu of the account: "Admin" or "Giocatore". The page then shows the new role. An admin can change their own role too.

- A change takes effect on the next request of that user, in the session already open. A demoted admin loses the admin actions at once and sees the not authorized page.
- Promoting a player to admin cancels the open [invite links](invite-links.md) of that player.
- The app always keeps at least one admin. When you set the role of the only admin to "Giocatore", the page shows "Serve almeno un admin" and the role stays "Admin".

## When no admin can sign in

An operator with access to the API host can [promote an account or reset a password](../developer-guide/setup/README.md#commands-on-the-api-host) from the command line. This is also the only way to reset the password of an admin.
