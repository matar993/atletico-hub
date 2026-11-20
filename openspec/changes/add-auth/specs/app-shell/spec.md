# Spec Delta

## ADDED Requirements

### Requirement: Sections require login
Every section of the app SHALL require a signed-in user. Without a valid session the app SHALL open the login page, and after login SHALL return to the section the user asked for. The login page (`/login`) and the invite page (`/invite/<token>`) SHALL be open without login and SHALL render outside the layout.

#### Scenario: Open a section without a session
- **WHEN** a user without a session opens `/squad`
- **THEN** the app shows the login page, and after a successful login it shows the Rosa page

#### Scenario: Session ends while using the app
- **WHEN** the API answers 401 to a call made by a page
- **THEN** the app shows the login page

### Requirement: Login page
The login page SHALL ask for an email and a password, and SHALL show the error the API gives on a failed login. It SHALL say that a new player gets access through a link from the admin.

#### Scenario: Failed login
- **WHEN** a user submits a wrong password
- **THEN** the login page stays open and shows "Email o password non corretti"

### Requirement: Logout from the header
The header SHALL show the first name and last name of the signed-in user and a logout button. Logout SHALL end the session and open the login page.

#### Scenario: Log out
- **WHEN** a signed-in user taps the logout button
- **THEN** the app shows the login page, and opening any section again shows the login page

## MODIFIED Requirements

### Requirement: Placeholder pages
Each section except Rosa SHALL show a page with a title equal to its label, one line that says what the section will be for, and an empty state. The pages SHALL show no real data and SHALL make no API call.

#### Scenario: Placeholder content
- **WHEN** the user opens Convocazioni
- **THEN** the page shows the heading "Convocazioni", a line that says it will hold the call-ups for the matches, and an empty state message
