## Context

State of `frontend/` after `add-base-ui-layout`: React 19, Tailwind CSS 4 (`@tailwindcss/vite`, `globals.css` holds only `@import 'tailwindcss'`), TanStack Router, `lucide-react`. Styling is plain slate utilities. The drawer is a native `<dialog>`.

Reference: `ai-os/frontend` keeps OKLCH tokens in CSS variables, a `.dark` class that redefines them, `framer-motion` for the active marker (`layoutId`), Radix for tooltip and menus, and a `Page` component. This change reuses those ideas, not its code or its hover-expanding dock.

Constraints:
- Content-Security-Policy (`nginx/security-headers.conf`): scripts only from `'self'`, no inline script. Styles allow inline. Fonts fall back to `default-src 'self'`.
- Tests query by role and accessible name. Those contracts stay (see proposal).
- Phone first (CODE_GUIDELINES).

## Goals / Non-Goals

**Goals:**
- One token layer that drives every color, so a palette change touches one place.
- Light, dark and system themes, no flash on load.
- Navigation and drawer that feel polished and stay accessible.
- Reusable `Page` and `EmptyState` so later features start from a good base.

**Non-Goals:**
- Command palette, notification data, real Home data, authentication.
- A full component library. Only components a page needs now.
- Hover-expanding dock, aurora background, charts.
- New routes or API calls.

## Decisions

### Tokens: CSS variables in OKLCH, mapped with Tailwind `@theme`

`globals.css` defines `--background`, `--surface`, `--surface-raised`, `--foreground`, `--muted-foreground`, `--border`, `--primary`, `--primary-foreground`, `--accent`, `--ring` and status colors on `:root`, and redefines them under `.dark`. A `@theme inline` block maps them to Tailwind colors, so classes read `bg-surface text-foreground`. Components never use raw hex or slate classes.

Default palette (assumption, club colors unknown): deep blue primary, coral red accent, cool neutrals.

- Why: one place to rebrand; dark theme is a second set of values, not second set of classes.
- Alternative: Tailwind `dark:` variant on every class. Rejected: doubles every class, easy to forget one.

### Theme: three-way choice, `.dark` class on `<html>`, stored in `localStorage`

State lives in a small `theme` feature: a provider and `useTheme()` returning `{ choice, resolved, setChoice }`. `choice` is `light | dark | system`. `resolved` is `light | dark`. System follows `matchMedia('(prefers-color-scheme: dark)')`.

A tiny classic script `public/theme-init.js`, loaded in `<head>` before the CSS, reads `localStorage` and sets the class before first paint. It is a file, not inline code, because the CSP forbids inline scripts. Every storage access sits in `try/catch`.

- Why: the no-flash rule needs code that runs before React; a file satisfies the CSP with no header change.
- Alternative: apply the class in React. Rejected: first paint shows the wrong theme.
- Alternative: cookie read by nginx. Rejected: needs server logic for a cosmetic choice.

### Drawer: Radix Dialog, with `framer-motion`

Radix Dialog replaces the native `<dialog>`. It gives focus trap, Escape, outside click, `aria-modal` and an inert background. `framer-motion` slides the panel in. Under `prefers-reduced-motion` the slide is off (`MotionConfig reducedMotion="user"`).

This replaces the decision in `add-base-ui-layout` ("no dialog library, one component"). Its reason no longer holds: the app now has a second overlay (user-facing theme menu) and a shared overlay look.

Kept: hamburger `Apri il menu` with `aria-expanded`, close button `Chiudi il menu`, role `dialog`, closing on navigation.

Gain: jsdom cannot run `showModal()`, but it runs Radix. The drawer becomes unit-testable. Playwright still covers it in a real browser.

### Theme control: Radix DropdownMenu with radio items

A header button opens a menu with Chiaro, Scuro, Sistema as radio items. The button shows the icon of the active choice (sun, moon, monitor) and has the accessible name "Tema".

- Why: Radix gives keyboard and ARIA behavior for free.
- Alternative: a single toggle button (light/dark). Rejected: cannot express "follow the system".

### Sidebar: wide, fixed, animated marker

Desktop keeps the fixed sidebar of `add-base-ui-layout`. New look: brand block on top (mark with initials plus team name), section list, and a muted footer. The active entry gets a background pill that moves between entries with a shared `layoutId` in `framer-motion`.

The hover-expanding dock of `ai-os` is not used: it needs a reducer for pointer, focus and touch, and the app is used mostly on phones where a dock adds nothing.

Both sidebar and drawer render the same `NavMenu`. The `layoutId` marker uses a different id per container so two copies never fight.

### Page and EmptyState components

`Page` takes `eyebrow`, `title`, `description`, optional `actions`, children. It renders the single `h1`. `EmptyState` takes an icon, a title and text. `PlaceholderPage` is rewritten on both, so the five section pages change only through it.

`PlaceholderPage` keeps its props, so section pages and their tests keep working.

### Home overview

`HomePage` renders `Page` and three `Panel`s with static sample rows and an `Anteprima` badge. The sample data is a constant inside `src/home/`, not an API mock. It is deleted when the real feature lands.

- Why: shows how the final Home will look and tests the layout; the badge keeps it honest (spec: Sample content is marked).

### Fonts: `@fontsource`, self-hosted

Inter (400, 500, 600, 700) and JetBrains Mono (400, 500) imported in `main.tsx`. Vite emits them as hashed files served from `'self'`, so the CSP needs no change. Only the Latin subset is imported to keep size down.

- Alternative: Google Fonts. Rejected: external request blocked by CSP and leaks visits.

### Class helper

`src/lib/cn.ts` exports `cn(...)` = `twMerge(clsx(...))`. Used by components that accept a `className`.

### Dependencies

| Package | Why |
|---|---|
| `framer-motion` | active marker, drawer slide, panel entrance |
| `@radix-ui/react-dialog` | drawer |
| `@radix-ui/react-dropdown-menu` | theme menu |
| `@fontsource/inter`, `@fontsource/jetbrains-mono` | self-hosted fonts |
| `tailwind-merge`, `clsx` | `cn()` |

Radix packages are installed one by one, only the two used. `framer-motion` imports only `motion`, `MotionConfig` and `AnimatePresence`. Bundle size is checked in the build task.

### ADR

No ADR. ADR-0003 fixes Tailwind for styles and does not forbid component or animation libraries. The libraries are web-app internal and reversible. If the app later shares a design system across projects, record it then.

### Folder structure

```
frontend/src/
  styles/globals.css        tokens, base styles, @theme mapping
  lib/cn.ts                 class helper
  theme/                    ThemeProvider, useTheme, ThemeMenu
  layout/                   AppLayout, NavMenu, Sidebar brand, Page, EmptyState, PlaceholderPage
  home/                     HomePage, Panel, sample content
frontend/public/theme-init.js
```

### Tests

- Unit (Vitest): `useTheme` (default system, choice saved, system change, storage throws); `ThemeMenu` (three choices, selecting sets `.dark`); `NavMenu`, `AppLayout`, `PlaceholderPage` existing tests pass unchanged; drawer open, navigate, close on Escape, runs in jsdom now; `HomePage` three panels and `Anteprima` labels; `Page` renders one `h1`.
- Browser (Playwright): existing navigation specs pass unchanged; theme choice survives reload with no wrong-theme first paint (check class on `<html>` right after navigation); drawer on phone viewport; run with the production CSP, so a blocked font or script fails the test.
- Accessibility: contrast checked for both themes on the token pairs (task 2.2), keyboard path through the theme menu in Playwright.

## Risks / Trade-offs

- [Bundle grows with `framer-motion`] → import only needed parts; measure `make ui-build` before and after; report the delta in the pull request.
- [Flash of wrong theme] → blocking `theme-init.js` in `<head>`; Playwright asserts it.
- [CSP blocks a new asset] → fonts are bundled files; e2e runs on the production image with its headers.
- [Existing tests break on markup change] → contracts kept (role, name, `aria-current`); run the old tests unchanged first.
- [Palette is a guess] → everything flows from tokens; the user reviews the screens and one file changes.
- [Sample content mistaken for real] → `Anteprima` badge, spec requirement, and no API call.
- [Radix and `add-base-ui-layout` drawer decision conflict] → documented above as superseded.

## Open Questions

- Official club colors (hex). Not blocking: defaults are used until given.
