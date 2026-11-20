# Spec Delta

## Purpose

Gives the web app its frame: a header, a navigation menu that works on a phone and on a wide screen, and the list of sections that every page of the app belongs to.

## ADDED Requirements

### Requirement: Sections of the app
The web app SHALL offer these sections, each at its own path, in this menu order: Home (`/`), Eventi (`/events`), Convocazioni (`/call-ups`), Rosa (`/squad`), Notifiche (`/notifications`), Profilo (`/profile`). Every section label SHALL be in Italian.

#### Scenario: Open a section by its path
- **WHEN** the user opens `/squad` directly in the browser
- **THEN** the app shows the layout with the Rosa page in the content area

#### Scenario: Menu lists every section
- **WHEN** the user opens the menu
- **THEN** the menu shows the six sections in the order above, each with an icon and its label

### Requirement: Layout of every page
Every page SHALL render inside one layout: a header at the top that shows the team name, the navigation menu, and a content area that shows the current section.

#### Scenario: Header shows the team name
- **WHEN** the user opens any section
- **THEN** the header shows the team name "Atletico San Lorenzo"

### Requirement: Navigate between sections
Choosing a menu entry SHALL show its section in the content area without a full page reload, and SHALL update the browser address to the section path.

#### Scenario: Move to another section
- **WHEN** the user is on Home and chooses "Eventi" in the menu
- **THEN** the content area shows the Eventi page and the address is `/events`

### Requirement: Active section highlighted
The menu entry of the current section SHALL be highlighted, and SHALL be marked as the current page for assistive technologies. Only one entry SHALL be active at a time.

#### Scenario: Only the current entry is active
- **WHEN** the user is on `/events`
- **THEN** the "Eventi" entry is highlighted and marked as current, and the "Home" entry is not

### Requirement: Fixed sidebar on a wide screen
On a wide screen the menu SHALL be a sidebar fixed on the left of the content area, always visible, and the header SHALL show no menu button.

#### Scenario: Sidebar visible on desktop
- **WHEN** the user opens the app on a desktop-width screen
- **THEN** the menu is visible on the left without any action, and no hamburger button is shown

### Requirement: Drawer on a phone
On a narrow screen the menu SHALL be hidden and SHALL open as a drawer from a hamburger button in the header. The drawer SHALL close when the user chooses an entry, presses Escape, uses its close button, or taps outside it. While the drawer is open, the page behind it SHALL not be reachable by keyboard.

#### Scenario: Open the drawer and navigate
- **WHEN** the user on a phone taps the hamburger button and chooses "Rosa"
- **THEN** the drawer opens with the menu, then closes, and the content area shows the Rosa page

#### Scenario: Close the drawer without navigating
- **WHEN** the drawer is open and the user presses Escape
- **THEN** the drawer closes and the current section does not change

#### Scenario: Menu hidden by default on a phone
- **WHEN** the user opens the app on a phone-width screen
- **THEN** the menu is not visible and the header shows the hamburger button

### Requirement: Placeholder pages
Each section SHALL show a page with a title equal to its label, one line that says what the section will be for, and an empty state. The pages SHALL show no real data and SHALL make no API call.

#### Scenario: Placeholder content
- **WHEN** the user opens Convocazioni
- **THEN** the page shows the heading "Convocazioni", a line that says it will hold the call-ups for the matches, and an empty state message
