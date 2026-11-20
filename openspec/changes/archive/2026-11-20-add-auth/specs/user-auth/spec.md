# Spec Delta

## Purpose

Lets the players of the squad sign in with an email and a password, keeps them signed in through a session, and keeps everyone else out of the API.

## ADDED Requirements

### Requirement: Account of a player
An account SHALL belong to exactly one player of the squad, and a player SHALL have at most one account. An account SHALL have an email, a password and a role, `admin` or `player`. Emails SHALL be unique without regard to letter case, and the API SHALL store and show them in lower case.

#### Scenario: Email unique without regard to case
- **WHEN** an account with the email `mario@example.com` exists and someone tries to create an account with `Mario@Example.com`
- **THEN** the API refuses it because the email is already in use

#### Scenario: One account per player
- **WHEN** a player already has an account
- **THEN** the API creates no second account for that player

### Requirement: Password rules
A password SHALL have at least 8 characters and at most 128. The API SHALL apply no other composition rule. The API SHALL store only a slow salted hash of the password, never the password itself.

#### Scenario: Short password refused
- **WHEN** a user chooses a password of 7 characters
- **THEN** the API refuses it and says the password needs at least 8 characters

#### Scenario: Password without digits or symbols accepted
- **WHEN** a user chooses the password `calcetto del martedi`
- **THEN** the API accepts it

### Requirement: Login with email and password
The API SHALL sign a user in when the email matches an account without regard to letter case and the password is correct, and SHALL then start a session. A wrong email and a wrong password SHALL give the same error, so the response does not tell whether the email has an account.

#### Scenario: Correct credentials
- **WHEN** a user logs in with the email and password of their account
- **THEN** the API starts a session and answers with the user's name and role

#### Scenario: Wrong password
- **WHEN** a user logs in with a correct email and a wrong password
- **THEN** the API answers 401 with the message "Email o password non corretti" and starts no session

#### Scenario: Unknown email
- **WHEN** a user logs in with an email that has no account
- **THEN** the API answers with the same status and message as for a wrong password

### Requirement: Login lockout
After 5 failed logins in a row on one account, the API SHALL refuse every login on that account for 15 minutes, even with the correct password. A successful login SHALL reset the count of failed logins.

#### Scenario: Fifth failure locks the account
- **WHEN** a user fails the login on one account 5 times in a row and then tries again with the correct password
- **THEN** the API answers 429 with the message "Troppi tentativi, riprova tra 15 minuti" and starts no session

#### Scenario: Lock expires
- **WHEN** 15 minutes have passed since the account was locked and the user logs in with the correct password
- **THEN** the API starts a session

#### Scenario: Success resets the count
- **WHEN** a user fails the login 4 times, then logs in, logs out and fails once more
- **THEN** the account is not locked

### Requirement: Session
A session SHALL be held by an httpOnly cookie with `SameSite=Lax` that carries a random token, and the API SHALL store only a hash of the token. A session SHALL expire 30 days after its last use. Each authenticated request SHALL extend it to 30 days from that request.

#### Scenario: Session extended by use
- **WHEN** a user makes a request 20 days after the last one
- **THEN** the session is valid and now expires 30 days after this request

#### Scenario: Session expired
- **WHEN** a user makes a request 31 days after the last one
- **THEN** the API answers 401 and the session is no longer valid

### Requirement: Logout
The API SHALL end the current session on logout and SHALL clear the session cookie.

#### Scenario: Request after logout
- **WHEN** a user logs out and then calls the API with the same cookie
- **THEN** the API answers 401

### Requirement: Current user
The API SHALL answer a request for the current user with the name of their player, their email and their role, or with 401 when the request has no valid session.

#### Scenario: Signed-in user
- **WHEN** a signed-in admin asks for the current user
- **THEN** the API answers with their first name, last name, email and the role `admin`

#### Scenario: No session
- **WHEN** a request without a session cookie asks for the current user
- **THEN** the API answers 401

### Requirement: API closed without a session
Every API route SHALL answer 401 to a request without a valid session, except the health check, login, and the invite routes.

#### Scenario: Route closed to anonymous requests
- **WHEN** a request without a session asks for the list of players
- **THEN** the API answers 401

#### Scenario: Health check stays open
- **WHEN** a request without a session calls the health check
- **THEN** the API answers 200

### Requirement: Protection against cross-site requests
Every request with the method POST, PUT, PATCH or DELETE SHALL carry the header `X-Requested-With: atletico-hub`. The API SHALL answer 403 to such a request without the header, before it applies any change. Login and the invite routes SHALL follow this rule too.

#### Scenario: Write without the header
- **WHEN** a signed-in user sends a POST request without the header `X-Requested-With`
- **THEN** the API answers 403 and changes nothing

#### Scenario: Read without the header
- **WHEN** a signed-in user sends a GET request without the header
- **THEN** the API answers normally

### Requirement: Admin-only actions
The API SHALL answer 403 when a user with the role `player` calls a route reserved for admins.

#### Scenario: Player calls an admin route
- **WHEN** a user with the role `player` asks to add a player to the squad
- **THEN** the API answers 403 and changes nothing

### Requirement: First admin
A command run on the API host SHALL create the first admin: a player with a first name and a last name, and an admin account with an email and a password. The command SHALL ask for the password without echoing it. The command SHALL refuse an email already in use.

#### Scenario: Create the first admin
- **WHEN** an operator runs the command with a name, an email and a valid password on an empty database
- **THEN** the squad has one player, that player has an admin account, and the admin can log in

#### Scenario: Email already in use
- **WHEN** an operator runs the command with an email that already has an account
- **THEN** the command fails with a message and creates nothing
