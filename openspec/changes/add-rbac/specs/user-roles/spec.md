# Spec Delta

## Purpose

Lets admins see every account with its role and change it, keeps at least one admin in the app, and gives the operator commands to recover an admin and to set a new password for any account.

## ADDED Requirements

### Requirement: List accounts
A user with `users:view` SHALL see every account: first name and last name of its player, email and role, sorted by last name and first name. Each account SHALL carry a flag that says whether the user may change its role.

#### Scenario: Admin lists accounts
- **WHEN** an admin asks for the list of accounts
- **THEN** the API answers every account with name, email, role and the flag to change the role

#### Scenario: Player cannot list accounts
- **WHEN** a user with role `player` asks for the list of accounts
- **THEN** the API answers 403

### Requirement: Change the role of an account
A user with `users:change_role` SHALL be able to set the role of any account, their own included, to `admin` or `player`. The role SHALL change only through this action.

#### Scenario: Admin promotes a player
- **WHEN** an admin sets the role of a player's account to `admin`
- **THEN** the account has role `admin`, and its next request has the admin permissions

#### Scenario: Admin demotes themselves
- **WHEN** one of two admins sets their own role to `player`
- **THEN** the API accepts it, and their next request has only the player permissions

#### Scenario: Unknown account
- **WHEN** an admin changes the role of an account that does not exist
- **THEN** the API answers 404

### Requirement: Last admin stays
The API SHALL refuse a role change that would leave the app with no account of role `admin`, with 409 and the message "Serve almeno un admin". Two role changes at the same time SHALL never leave the app with no admin.

#### Scenario: Demote the only admin
- **WHEN** the only admin sets their own role to `player`
- **THEN** the API answers 409 "Serve almeno un admin" and the role stays `admin`

#### Scenario: Two admins demote each other at once
- **WHEN** the only two admins each demote the other at the same moment
- **THEN** one change succeeds, the other answers 409, and one admin is left

### Requirement: Promotion cancels invite links
Promoting an account to `admin` SHALL cancel every open invite link of its player.

#### Scenario: Link created before promotion
- **WHEN** an admin creates an invite link for a player with an account, then promotes that account, then the link is opened
- **THEN** the app says the link is not valid

### Requirement: Users page
The Utenti page SHALL list every account with name, email and role, and SHALL offer a role choice on each account whose flag allows it. After a change the page SHALL show the new role. When the API refuses the change, the page SHALL show its message and keep the old role.

#### Scenario: Admin promotes from the page
- **WHEN** an admin opens Utenti and sets the role of "Luca Bianchi" to admin
- **THEN** the page shows "Luca Bianchi" with role admin

#### Scenario: Last admin refused on the page
- **WHEN** the only admin sets their own role to player on Utenti
- **THEN** the page shows "Serve almeno un admin" and their role stays admin

### Requirement: Promote an account from the command line
A command run on the API host SHALL set the role of the account with a given email to `admin`, even when no admin is left. It SHALL cancel the open invite links of that player. It SHALL fail with a message when no account has that email.

#### Scenario: Recover an admin
- **WHEN** the operator runs the command with the email of a player account
- **THEN** the account has role `admin` and can use the admin actions

#### Scenario: Unknown email
- **WHEN** the operator runs the command with an email that has no account
- **THEN** the command fails with a message and changes nothing

### Requirement: Reset a password from the command line
A command run on the API host SHALL set a new password for the account with a given email, asking for it without echoing it. It SHALL apply the password rules, end every session of the account and clear any login lockout. It SHALL fail with a message on an unknown email or an invalid password.

#### Scenario: Reset an admin password
- **WHEN** the operator runs the command with an admin's email and a valid password
- **THEN** the new password works, and the earlier sessions of that account end

#### Scenario: Short password
- **WHEN** the operator enters a password of 7 characters
- **THEN** the command fails with a message and the old password still works
