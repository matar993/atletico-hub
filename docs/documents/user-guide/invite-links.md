# Invite links

An invite link is a personal link that an admin gives to one player. The player uses it to create an account or to set a new password. The app sends no email: the admin sends the link, for example on WhatsApp.

Rules of every link:

- It belongs to one player.
- It works once.
- It is valid for 7 days from its creation.
- A new link for the same player cancels the earlier ones.
- An expired, used, cancelled or unknown link shows the same message: "Link non valido o scaduto. Chiedi un nuovo link all'admin."

## As a player

Open the link you received. The page greets you by name.

### Create your account

When you have no account, the page asks for an email and a password. The password needs 8 to 128 characters, with no other rule. Press "Crea account". You are signed in and the app opens Home.

When the email belongs to another account, the page shows "Email già in uso". The link stays valid: try another email.

### Set a new password

When you already have an account, the page shows your email and asks only for a new password. Press "Imposta la password". You are signed in, and every other session of your account ends.

## As an admin

Admins work on the Rosa page (`/squad`). A user with the role `player` does not see these actions.

### Add a player

1. Press "Aggiungi giocatore".
2. Enter first name and last name, 1 to 50 characters each.
3. Press "Aggiungi".

The player appears in the list as "Senza account".

### Rename a player

1. Press "Modifica nome" on the row of the player.
2. Change first name and last name, 1 to 50 characters each.
3. Press "Salva".

The list shows the new name at once. A player changes their own name on the [Profilo page](profile.md).

### Create a link

1. Press "Crea link d'invito" on the row of the player.
2. Copy the link with "Copia". The page confirms with "Link copiato".
3. Send the link to the player.

The page shows the link once, with its expiry date. After you leave the page, the link cannot be shown again: create a new one, which cancels this one.

The list shows the email of each player that has an account. Players see the list without emails.

### Reset a password

Create a new link for the player and send it. The player opens it and chooses a new password.

The row of a player whose account has the role `admin` has no "Crea link d'invito" button, and the API refuses to create one. An admin's password is reset only from the command line of the API host: see [commands on the API host](../developer-guide/setup/README.md#commands-on-the-api-host). Promoting a player to admin cancels the open links of that player.
