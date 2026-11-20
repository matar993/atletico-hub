# home-overview Specification

## Purpose
Defines the Home page as an overview of the areas of the app, using clearly marked sample content until real data exists.

## Requirements

### Requirement: Overview panels

Home SHALL show the heading "Home", one line saying what it is for, and one panel each for next events, call-ups and notifications. Each panel SHALL have a title, an icon and a link to its section.

#### Scenario: Panels visible
- **WHEN** the user opens Home
- **THEN** the page shows three panels titled "Prossimi eventi", "Convocazioni" and "Notifiche"

#### Scenario: Panel leads to its section
- **WHEN** the user chooses the link of the "Prossimi eventi" panel
- **THEN** the app shows the Eventi page and the address is `/events`

### Requirement: Sample content is marked

Content in a panel that is not real data SHALL carry the label "Anteprima". Home SHALL NOT show invented content as if it were real, and SHALL NOT call the API.

#### Scenario: Sample content label
- **WHEN** a panel shows sample rows
- **THEN** the panel shows the label "Anteprima" next to its title

### Requirement: Shared page heading

Every section page SHALL show its title as a level 1 heading, with a short eyebrow above it and one line of description below it.

#### Scenario: Section heading
- **WHEN** the user opens Rosa
- **THEN** the page shows the heading "Rosa" and its description line
