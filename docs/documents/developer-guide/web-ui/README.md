# Web app UI

How the look of the web app is built: design tokens, themes, components, contrast.

> **Source**: `frontend/src/styles/globals.css`, `frontend/public/theme-init.js`, `frontend/src/theme/`, `frontend/src/layout/`
> **Last update**: 2026-11-20 · **Scope**: design tokens, theme, adding a component, contrast · **Markers**: none

## Design tokens

`frontend/src/styles/globals.css` defines every color as a CSS variable in OKLCH on `:root` (light theme) and redefines it under `.dark` (dark theme). A `@theme inline` block maps the variables to Tailwind colors: components write `bg-surface text-foreground` and never raw colors. Changing the palette means editing this one file. The brand colors come from the club website: red `#e10b00` (`primary`) and navy `#060843` (dark theme backgrounds).

| Token | Use |
|---|---|
| `background`, `surface`, `surface-raised` | Page, cards and panels, raised elements |
| `foreground`, `muted-foreground` | Main text, secondary text |
| `border`, `ring` | Borders, focus outline |
| `primary`, `primary-foreground` | Main action color and the text on it |
| `accent`, `accent-foreground` | Soft highlight (active entry) and the text on it |
| `success`, `warning`, `danger` | Status colors, used as text on `background` or `surface` |

Fonts are Inter (400, 500, 600, 700) and JetBrains Mono (400, 500), self-hosted through `@fontsource` and imported in `frontend/src/main.tsx`.

## Theme

Light is the default of `:root`; dark is the `.dark` class on `<html>`. The choice (`light`, `dark`, `system`) is kept in `localStorage` under the key `theme`.

- `frontend/public/theme-init.js` runs in `<head>` before the CSS and sets the class before the first paint. It is a file, not inline code, because the Content-Security-Policy forbids inline scripts.
- `ThemeProvider` (`frontend/src/theme/`) keeps the choice in React, saves it, and follows the system when the choice is `system`. `useTheme` reads it. `ThemeMenu` is the header control.
- Every storage access sits in `try/catch`: when storage is blocked the app uses `system`.

## Add a component

1. Style it with token classes only (`bg-surface`, `text-muted-foreground`, `border-border`). Never write a raw color, and never use `dark:` variants: the tokens already change with the theme.
2. Accept `className` only when a caller needs it, and merge with `cn()` from `frontend/src/lib/cn.ts` (`twMerge(clsx(...))`).
3. Use `Page` and `EmptyState` (`frontend/src/layout/`) for a section page: one `h1`, eyebrow, description, actions.
4. Use Radix for overlays and menus (`@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`) and `framer-motion` for movement. The app wraps everything in `MotionConfig reducedMotion="user"`, so a slide turns off for users who ask for less motion.
5. Add a unit test that queries by role and accessible name. Add a Playwright spec when behavior needs a real browser.
6. If the component adds a color pair, check it reaches 4.5:1 in both themes and add it to the table below.

## Contrast

Every foreground and background pair of the tokens must reach at least 4.5:1 (WCAG AA for text) in both themes. Ratios of the current palette:

| Theme | Pair | Ratio |
|---|---|---|
| light | `foreground on background` | 17.96 |
| light | `foreground on surface` | 18.75 |
| light | `foreground on surface-raised` | 16.93 |
| light | `muted-foreground on background` | 7.17 |
| light | `muted-foreground on surface` | 7.48 |
| light | `muted-foreground on surface-raised` | 6.76 |
| light | `primary-foreground on primary` | 4.93 |
| light | `accent-foreground on accent` | 6.85 |
| light | `primary on background` | 4.73 |
| light | `primary on surface` | 4.93 |
| light | `success on background` | 6.74 |
| light | `success on surface` | 7.04 |
| light | `warning on background` | 5.89 |
| light | `warning on surface` | 6.15 |
| light | `danger on background` | 6.39 |
| light | `danger on surface` | 6.67 |
| dark | `foreground on background` | 18.49 |
| dark | `foreground on surface` | 17.74 |
| dark | `foreground on surface-raised` | 16.34 |
| dark | `muted-foreground on background` | 9.37 |
| dark | `muted-foreground on surface` | 8.99 |
| dark | `muted-foreground on surface-raised` | 8.28 |
| dark | `primary-foreground on primary` | 5.76 |
| dark | `accent-foreground on accent` | 12.24 |
| dark | `primary on background` | 5.89 |
| dark | `primary on surface` | 5.65 |
| dark | `success on background` | 10.67 |
| dark | `success on surface` | 10.24 |
| dark | `warning on background` | 11.41 |
| dark | `warning on surface` | 10.94 |
| dark | `danger on background` | 7.94 |
| dark | `danger on surface` | 7.61 |
