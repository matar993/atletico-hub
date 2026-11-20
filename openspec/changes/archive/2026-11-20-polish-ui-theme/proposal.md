## Why

The web app works but looks bare: white page, grey borders, one font weight, no theme, flat placeholder pages. Players and staff open it mostly from a phone, so first impression and feel matter. The sibling project `ai-os` has a polished UI (design tokens, light and dark theme, animated navigation, clear page headings). This change brings the same level of polish to Atletico Hub with its own identity.

## What Changes

- Add a design-token layer (OKLCH colors, radii, shadows, fonts) in `globals.css`, exposed to Tailwind, with a light and a dark theme.
- Add a theme control in the header: Chiaro, Scuro, Sistema. The choice is saved in the browser. Default is the system preference. No flash of the wrong theme on load.
- Restyle the shell: sticky header with brand mark, wide fixed sidebar with an animated active marker, drawer on phone that slides in.
- Replace the native `<dialog>` drawer with Radix Dialog (**BREAKING for the design only**: replaces the choice in `add-base-ui-layout`; accessible names, roles and behavior stay the same).
- Add a shared `Page` component (eyebrow, title, description, actions) and a restyled empty state. All section pages use them.
- Turn Home into an overview with panels (next events, call-ups, notifications). Panel content is static sample content, marked "Anteprima". No API call.
- Self-host Inter and JetBrains Mono.
- Keep every existing contract: paths, menu order and labels, accessible names (`Menu principale`, `Apri il menu`, `Chiudi il menu`), `aria-current`, page headings, team name in the header.

## Capabilities

### New Capabilities

- `app-theme`: light, dark and system themes, the control that switches them, and how the choice is kept.
- `home-overview`: the Home page as an overview of panels with clearly marked sample content.

### Modified Capabilities

None. `app-shell` is defined by the not yet archived change `add-base-ui-layout`, so there is no main spec to modify. Its behavior does not change.

## Impact

- Code: `frontend/src/` (layout, home, styles, new `lib/cn.ts`, theme feature), `frontend/index.html`, `frontend/public/` (one small script), `frontend/e2e/`.
- Dependencies added to `frontend/package.json`: `framer-motion`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@fontsource/inter`, `@fontsource/jetbrains-mono`, `tailwind-merge`, `clsx`.
- No backend change, no API change.
- Docs: user guide (navigation, theme), `ARCHITECTURE.md` "Today" section, developer guide (design tokens, how to add a component).
- No project-wide decision: ADR-0003 already names Tailwind CSS for styles. The added libraries stay inside the web app and are recorded in `design.md`.
- Ordering: this change builds on `add-base-ui-layout`. Archive that change first, or archive both in the same pull request.
- Open point: the club colors are not known. Default palette is deep blue (primary) and coral red (accent). It is an assumption, changeable in one place (the tokens).
