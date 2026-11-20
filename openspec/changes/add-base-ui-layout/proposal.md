# Proposal

## Why

The web app shows only a heading with the team name: there is no layout and no way to move between the parts of the app. Every next feature (events, call-ups, squad, notifications, profile) needs a place to live, so the app needs its shell first: a layout, a menu and one page per section, built for a phone screen.

## What Changes

- Add the app shell: a header with the team name (placeholder), a vertical menu with an icon and a label per section, and a content area where the pages load.
- On a phone the menu is a drawer, opened by a hamburger button in the header. On a wide screen the menu is a fixed sidebar on the left. The active section is highlighted.
- Add six placeholder pages: Home, Eventi, Convocazioni, Rosa, Notifiche, Profilo. Each one has a title, a line that says what it will be for, and an empty state. No real data and no API calls.
- Keep the menu entries (label, path, icon) in one configuration, so a new section is one entry plus its page.
- UI texts are in Italian; code names, components and paths are in English.
- The home page heading changes from the team name to "Home": the team name moves to the header. The existing unit and browser tests on the home page change with it.
- Add one runtime dependency for the icons (see design.md).

## Capabilities

### New Capabilities

- `app-shell`: the layout of the web app, its navigation menu (sidebar and drawer) and the list of sections it leads to.

### Modified Capabilities

None.

## Impact

- Code: `frontend/src/` only (routes, a new layout feature, one page per section, tests), `frontend/e2e/`, `frontend/index.html` (document language set to Italian).
- Dependencies: `lucide-react` added to `frontend/package.json`.
- No backend change, no API change, no new route on the API.
- Docs: a user guide page for the navigation, the "Today" section of `ARCHITECTURE.md`.
- No project-wide decision: the stack of ADR-0003 (React, TanStack Router, Tailwind CSS) is reused as is.
