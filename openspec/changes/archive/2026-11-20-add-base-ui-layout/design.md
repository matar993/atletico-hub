# Design

## Context

What the web app has today (`frontend/`):

- React 19, TypeScript, Vite 7, on the stack of ADR-0003.
- TanStack Router with file-based routes: `@tanstack/router-plugin` generates `src/routeTree.gen.ts` from `src/routes/` (`autoCodeSplitting: true`). `__root.tsx` wraps the pages in a `<main>`; `index.tsx` renders `src/home/HomePage.tsx`.
- Tailwind CSS 4 through `@tailwindcss/vite`, imported once in `src/styles/globals.css`. No component library, no icon library.
- ESLint with `typescript-eslint`, `jsx-a11y` and `react-hooks`; Prettier; Vitest with Testing Library on jsdom; Playwright on the production build, with the image's Content-Security-Policy (scripts from `'self'` only, inline styles allowed).
- Code is grouped by feature (`src/<feature>/`); routes stay thin and import the page of their feature (CODE_GUIDELINES.md).
- `index.html` declares `lang="en"`.

## Goals / Non-Goals

**Goals:**

- One layout component for every page, driven by one menu configuration.
- A drawer that is accessible without a dialog library: focus kept inside, Escape closes it, the page behind is inert.
- Reuse the router, the CSS tool and the test tools already in the repository.

**Non-Goals:**

- Authentication, roles, or hiding sections per user.
- A theme, dark mode, or a design system beyond Tailwind utility classes.
- Real team name from configuration or from the API: the name is a constant for now.
- Badges or counters on menu entries (for example unread notifications).

## Decisions

### Router: TanStack Router, file-based, root route renders the layout

`src/routes/__root.tsx` renders `AppLayout`, which places `<Outlet />` in the content area. One thin route file per section (`index.tsx`, `events.tsx`, `call-ups.tsx`, `squad.tsx`, `notifications.tsx`, `profile.tsx`) imports the page of its feature.

- Why: the router is already installed and generates typed paths; the root route is its intended place for a shared layout.
- Alternative: a pathless layout route (`_layout.tsx`). Rejected: every page uses the same layout today, so a second level adds nothing.

### Paths in English, labels in Italian

Paths: `/`, `/events`, `/call-ups`, `/squad`, `/notifications`, `/profile`. Labels: Home, Eventi, Convocazioni, Rosa, Notifiche, Profilo. This follows the request: code names and paths in English, UI texts in Italian.

### Menu configuration in one module

`src/layout/navigation.ts` exports one ordered array of entries `{ label, to, icon }`. Both the sidebar and the drawer render the same `NavMenu` component from this array. `to` is typed with the router's registered paths, so an entry for a path without a route fails the type check.

- Adding a section: add the route file, the page, and one entry in the array.
- Why not derive the menu from the route tree (route `staticData`): it spreads the menu over six files and makes the order implicit. The request asks for one place.

### Icons: `lucide-react`

One new runtime dependency. Icons are React components rendering inline SVG.

- Why: ES modules with tree shaking, so the bundle holds only the six icons used (about 1 KB each); typed props; consistent stroke style; no font or external request, so the image's Content-Security-Policy needs no change; widely used and maintained.
- Alternative 1: hand-written inline SVG components. No dependency, but every new section needs someone to draw or copy an icon and keep the style consistent.
- Alternative 2: `@heroicons/react`. Equivalent weight and quality, smaller set (no clear icon for call-ups or a squad). Lucide has `House`, `CalendarDays`, `ClipboardList`, `Users`, `Bell`, `CircleUser`, plus `Menu` and `X` for the drawer buttons.
- Alternative 3: an icon font. Rejected: a font file to load, worse accessibility, no tree shaking.

### Drawer: native `<dialog>` with `showModal()`, no UI library

On a narrow screen the header shows a hamburger button that opens a `<dialog>` element holding `NavMenu`. `showModal()` gives, from the browser itself: focus moved into the dialog and kept there, the rest of the page inert, Escape to close, and the `::backdrop`. The component adds: close on backdrop click, a close button, close on entry click, and `aria-expanded` / `aria-controls` on the hamburger button.

- Why: zero dependencies and the accessibility the spec asks for (page behind unreachable by keyboard), which a plain `<div>` with CSS would not give without a focus-trap library.
- Alternative: Radix UI Dialog or Headless UI. Rejected for now: a dependency for one component; can be reconsidered when the app needs several overlays (menus, modals, toasts).

### Breakpoint: `md` (768 px)

Below `md` the sidebar is hidden (`hidden md:flex`) and the hamburger button shows (`md:hidden`); from `md` up the sidebar is fixed and the button hides. Mobile-first: base classes describe the phone, `md:` classes add the wide layout.

- Why `md`: a tablet in portrait has room for a 16 rem sidebar next to the content; the target device is the phone either way.

### Active entry

`NavMenu` uses the router's `Link` with `activeProps` for the highlight classes. `Link` sets `aria-current="page"` on the active link, which the tests query. The Home entry uses `activeOptions: { exact: true }`, otherwise `/` would match every path.

### Folder structure

```
frontend/src/
  layout/                 shell of the app
    AppLayout.tsx         header, sidebar, drawer, content area
    NavMenu.tsx           list of menu entries, shared by sidebar and drawer
    navigation.ts         the menu configuration and the team name constant
    PlaceholderPage.tsx   title, description, empty state
    *.test.tsx
  home/HomePage.tsx       one folder per section, as the feature will grow there
  events/EventsPage.tsx
  call-ups/CallUpsPage.tsx
  squad/SquadPage.tsx
  notifications/NotificationsPage.tsx
  profile/ProfilePage.tsx
  routes/                 thin route files, one per section
```

Each section page renders `PlaceholderPage` with its Italian texts. A folder per section looks heavy for one file each, but it is the feature-first layout of CODE_GUIDELINES.md and where each feature will grow. `PlaceholderPage` lives in `layout/` because every section uses it and it will disappear as the features arrive.

### Document language

`index.html` changes `lang="en"` to `lang="it"`: the UI is in Italian, and screen readers pick the pronunciation from it.

### Tests

- Unit (Vitest): `NavMenu` renders every entry of the configuration in order with its accessible name, and marks only the current one with `aria-current`; `PlaceholderPage` renders title, description and empty state; `AppLayout` shows the team name and the content of the current route. Tests mount a router with a memory history.
- Browser (Playwright): navigation through all sections on a desktop viewport; drawer open, navigate, close on Escape on a phone viewport. The drawer is tested here because jsdom does not implement `HTMLDialogElement.showModal()`.
- The existing `HomePage.test.tsx` and `e2e/home.spec.ts` expect the team name as the home heading; they are rewritten for the new layout.

## Risks / Trade-offs

- [jsdom lacks `showModal()`] → drawer behavior is covered by Playwright; unit tests do not open the drawer.
- [`<dialog>` styling differs between browsers (backdrop, default margins)] → reset its default styles with Tailwind classes and check on the Playwright Chromium phone viewport; Safari on iOS supports `showModal()` since 15.4.
- [Placeholder folders and pages are replaced feature by feature] → accepted; the shape matches where the code will go, so later changes edit, not move.
- [One more runtime dependency] → small and tree-shaken; Dependabot already watches `frontend/`.
