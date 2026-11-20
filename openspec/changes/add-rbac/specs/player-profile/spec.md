# Spec Delta

## Purpose

Lets every signed-in user see their own profile and change their own data, on the Profilo page, without reaching the data of any other player.

## ADDED Requirements

### Requirement: Change one's own name
A user with `profile:update` SHALL be able to change the first name and last name of their own player, with the same rules as when a player is added. The action SHALL always apply to the player of the signed-in account and SHALL take no player id.

#### Scenario: Player changes their own name
- **WHEN** a user with the role `player` changes their own last name from "Bianchi" to "Bianchi Rossi"
- **THEN** the current user and the squad show "Bianchi Rossi"

#### Scenario: Empty name refused
- **WHEN** a user changes their own first name to only spaces
- **THEN** the API answers 422 and the name does not change

### Requirement: Profilo page
The Profilo page SHALL show the first name, last name, email and role of the signed-in user, and a form to change first name and last name. After a save the page and the header SHALL show the new name. When the API refuses the change, the page SHALL show its message and keep the old name.

#### Scenario: Save a new name
- **WHEN** a user opens Profilo, changes the first name to "Luca" and saves
- **THEN** the page and the header show "Luca"

#### Scenario: Refused name
- **WHEN** a user saves an empty first name
- **THEN** the page shows the API message and the header keeps the old name
