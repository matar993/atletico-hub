# Navigation

How to move between the sections of the web app.

## Sections

The menu lists six sections, in this order:

| Section | Path |
|---|---|
| Home | `/` |
| Eventi | `/events` |
| Convocazioni | `/call-ups` |
| Rosa | `/squad` |
| Notifiche | `/notifications` |
| Profilo | `/profile` |

Every section needs a [login](login.md). Rosa lists the players of the squad ([invite links](invite-links.md) explains the admin actions). The other sections show a title, one line that says what they will be for, and an empty state. They show no real data yet, except Home, which shows [panels with sample content](#home).

The header stays at the top while you scroll. It shows the team name, "Atletico San Lorenzo", your name, the theme control and the logout button. The section you are in is highlighted in the menu.

## Home

Home shows three panels: "Prossimi eventi", "Convocazioni" and "Notifiche". The title of each panel is a link to its section. The content of the panels is sample content, not data of the team: each panel carries the label "Anteprima".

## Theme

The theme button in the header ("Tema") opens a menu with three choices:

| Choice | Effect |
|---|---|
| Chiaro | Light theme |
| Scuro | Dark theme |
| Sistema | Follows the theme of your device, and changes when the device changes |

Without a choice, the app follows the device. The choice is kept in the browser and applies from the first moment the page shows. If the browser blocks storage, the app still works and follows the device. When the device asks for reduced motion, the drawer appears without sliding.

## On a wide screen

The menu is a fixed sidebar on the left. It is always visible. The header has no menu button.

## On a phone

The menu is hidden. Tap the hamburger button in the header to open it as a drawer. The drawer closes when you:

- choose a section,
- press Escape,
- tap the close button,
- tap outside the drawer.

While the drawer is open, the page behind it cannot be reached with the keyboard.
