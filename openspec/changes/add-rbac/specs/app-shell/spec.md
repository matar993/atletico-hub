# Spec Delta

## MODIFIED Requirements

### Requirement: Sections of the app
The web app SHALL offer these sections, each at its own path, in this menu order: Home (`/`), Eventi (`/events`), Convocazioni (`/call-ups`), Rosa (`/squad`), Notifiche (`/notifications`), Profilo (`/profile`), Utenti (`/users`). The menu SHALL show Utenti only to a user with the role `admin`. Every section label SHALL be in Italian.

#### Scenario: Open a section by its path
- **WHEN** the user opens `/squad` directly in the browser
- **THEN** the app shows the layout with the Rosa page in the content area

#### Scenario: Menu lists every section
- **WHEN** an admin opens the menu
- **THEN** the menu shows the seven sections in the order above, each with an icon and its label

#### Scenario: Menu of a player
- **WHEN** a user with the role `player` opens the menu
- **THEN** the menu shows the first six sections and no Utenti entry

### Requirement: Placeholder pages
Each section except Rosa, Profilo and Utenti SHALL show a page with a title equal to its label, one line that says what the section will be for, and an empty state. The pages SHALL show no real data and SHALL make no API call.

#### Scenario: Placeholder content
- **WHEN** the user opens Convocazioni
- **THEN** the page shows the heading "Convocazioni", a line that says it will hold the call-ups for the matches, and an empty state message

## ADDED Requirements

### Requirement: Not authorized page
A user who opens a section they may not use SHALL see, inside the layout, a page that says "Non hai i permessi per vedere questa pagina", with a link to Home. The page SHALL make no call to the API of that section.

#### Scenario: Player opens Utenti by its path
- **WHEN** a user with the role `player` opens `/users` directly in the browser
- **THEN** the app shows the layout with the not authorized page and a link to Home
