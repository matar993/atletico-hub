# player-invites Specification

## Purpose
Lets an admin hand a player of the squad a personal link, through which the player creates their account or sets a new password, without any email sent by the app.

## Requirements

### Requirement: Create an invite link
An admin SHALL be able to create an invite link for any player of the squad. The link SHALL carry a random token, and the API SHALL store only a hash of it. The API SHALL show the link only once, in the answer that creates it.

#### Scenario: Admin creates a link
- **WHEN** an admin creates an invite link for a player
- **THEN** the API answers with a link of the form `/invite/<token>` and its expiry date

#### Scenario: Player cannot create a link
- **WHEN** a user with the role `player` asks for an invite link
- **THEN** the API answers 403

### Requirement: One valid link per player
A new invite link for a player SHALL cancel every earlier link of that player.

#### Scenario: Old link cancelled
- **WHEN** an admin creates a link for a player, then creates a second one, and the player opens the first
- **THEN** the app says the link is not valid

### Requirement: Link validity
An invite link SHALL be valid for 7 days from its creation and SHALL work only once. An expired, used, cancelled or unknown link SHALL give the same answer: the link is not valid.

#### Scenario: Expired link
- **WHEN** a player opens a link created 8 days ago
- **THEN** the app shows "Link non valido o scaduto. Chiedi un nuovo link all'admin."

#### Scenario: Used link
- **WHEN** a player completes the invite and then opens the same link again
- **THEN** the app shows the same message as for an expired link

### Requirement: Open an invite link
Opening a valid link SHALL show the first name and last name of the player it belongs to, and SHALL say whether the player creates an account or sets a new password.

#### Scenario: Player without an account
- **WHEN** a player without an account opens a valid link
- **THEN** the app greets them by name and asks for an email and a password

#### Scenario: Player with an account
- **WHEN** a player with an account opens a valid link
- **THEN** the app greets them by name, shows their email, and asks only for a new password

### Requirement: Create the account through the link
For a player without an account, completing a valid link with an email and a valid password SHALL create an account with the role `player`, SHALL use up the link, and SHALL start a session.

#### Scenario: Account created
- **WHEN** a player without an account completes the link with a free email and a password of 10 characters
- **THEN** the account exists with the role `player`, the player is signed in, and the app opens Home

#### Scenario: Email in use
- **WHEN** a player completes the link with an email that another account already uses
- **THEN** the API refuses it, creates no account, and the link stays valid

### Requirement: Reset the password through the link
For a player with an account, completing a valid link with a valid password SHALL replace the password, SHALL end every session of that account, SHALL clear any login lockout, SHALL use up the link, and SHALL start a new session. The email and the role SHALL not change.

#### Scenario: Password reset
- **WHEN** a player signed in on two phones completes a reset link from a third device
- **THEN** both earlier sessions end, the new password works, and the third device is signed in

#### Scenario: Lockout cleared
- **WHEN** an account is locked after 5 failed logins and its player completes a reset link
- **THEN** the player can log in with the new password at once
