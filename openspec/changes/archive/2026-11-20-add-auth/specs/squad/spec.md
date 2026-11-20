# Spec Delta

## Purpose

Holds the players of the squad, so that each account and each invite link belongs to a known player, and lists them on the Rosa page.

## ADDED Requirements

### Requirement: Player of the squad
A player SHALL have a first name and a last name, each between 1 and 50 characters after the spaces at the ends are removed.

#### Scenario: Empty name refused
- **WHEN** an admin adds a player whose first name is only spaces
- **THEN** the API refuses it and adds no player

### Requirement: Add a player
An admin SHALL be able to add a player to the squad with a first name and a last name. A user with the role `player` SHALL not.

#### Scenario: Admin adds a player
- **WHEN** an admin adds the player "Luca Bianchi"
- **THEN** the squad lists "Luca Bianchi" without an account

### Requirement: List the squad
Every signed-in user SHALL see the list of players, sorted by last name and then first name. For each player the list SHALL say whether the player has an account. Only an admin SHALL see the account email of each player.

#### Scenario: Player sees the squad
- **WHEN** a user with the role `player` opens Rosa
- **THEN** the page lists every player by name, and shows no email and no admin action

#### Scenario: Admin sees the squad
- **WHEN** an admin opens Rosa
- **THEN** the page lists every player with the email of their account, if any, a button to add a player, and a button per player to create an invite link

### Requirement: Share an invite link from Rosa
After an admin creates an invite link on Rosa, the page SHALL show the full link with a button to copy it, and its expiry date. The page SHALL warn that the link is shown only once.

#### Scenario: Copy the link
- **WHEN** an admin creates a link for "Luca Bianchi" and taps the copy button
- **THEN** the full link is in the clipboard and the page confirms the copy
