# Spec Delta

## MODIFIED Requirements

### Requirement: Create an invite link
An admin SHALL be able to create an invite link for any player of the squad whose account, if any, does not have the role `admin`. The link SHALL carry a random token, and the API SHALL store only a hash of it. The API SHALL show the link only once, in the answer that creates it.

#### Scenario: Admin creates a link
- **WHEN** an admin creates an invite link for a player
- **THEN** the API answers with a link of the form `/invite/<token>` and its expiry date

#### Scenario: Player cannot create a link
- **WHEN** a user with the role `player` asks for an invite link
- **THEN** the API answers 403

#### Scenario: No link for an admin account
- **WHEN** an admin asks for an invite link for a player whose account has the role `admin`, their own included
- **THEN** the API answers 403 with the message "La password di un admin si reimposta solo da riga di comando" and creates no link

#### Scenario: Link for a demoted admin
- **WHEN** an admin asks for an invite link for a player whose account was admin and now has the role `player`
- **THEN** the API creates the link
