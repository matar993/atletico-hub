# app-theme Specification

## Purpose
Defines the visual themes of the web app (light, dark, system), the control that switches them, and how the choice is kept between visits.

## Requirements

### Requirement: Light and dark themes

The app SHALL offer a light theme and a dark theme. Text and interactive elements SHALL keep a contrast ratio of at least 4.5:1 against their background in both themes.

#### Scenario: Dark theme applied
- **WHEN** the dark theme is active
- **THEN** the page, header, sidebar and content use dark surfaces and light text

### Requirement: Theme choice

The header SHALL show a control with three choices: Chiaro, Scuro, Sistema. Choosing Sistema SHALL follow the operating system preference and SHALL react when that preference changes.

#### Scenario: Choose dark theme
- **WHEN** the user opens the theme control and chooses "Scuro"
- **THEN** the dark theme is applied at once, without a page reload

#### Scenario: Follow the system
- **WHEN** the user chose "Sistema" and the operating system switches to dark
- **THEN** the app switches to the dark theme

### Requirement: Default theme

On first visit, with no saved choice, the app SHALL use "Sistema".

#### Scenario: First visit on a dark system
- **WHEN** a user with no saved choice opens the app on a system set to dark
- **THEN** the app shows the dark theme

### Requirement: Theme persistence

The app SHALL keep the choice in the browser and SHALL apply it before the first paint, so the page never flashes the wrong theme. If the browser cannot store it, the app SHALL still work and use "Sistema".

#### Scenario: Choice survives a reload
- **WHEN** the user chooses "Scuro" and reloads the page
- **THEN** the dark theme is shown from the first paint

#### Scenario: Storage unavailable
- **WHEN** the browser blocks storage and the user opens the app
- **THEN** the app renders with the system theme and no error

### Requirement: Reduced motion

When the user prefers reduced motion, the app SHALL NOT play slide or movement animations. State changes SHALL still be visible.

#### Scenario: Reduced motion preference
- **WHEN** the operating system asks for reduced motion and the user opens the menu drawer
- **THEN** the drawer appears without a sliding animation
