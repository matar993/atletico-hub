# Web app UI

How the look of the web app is built: design tokens, themes, contrast.

> **Source**: `frontend/src/styles/globals.css`
> **Last update**: 2026-11-20 · **Scope**: design tokens, contrast · **Markers**: palette is a default until the official club colors are given

## Design tokens

`frontend/src/styles/globals.css` defines every color as a CSS variable in OKLCH on `:root` (light theme) and redefines it under `.dark` (dark theme). A `@theme inline` block maps the variables to Tailwind colors: components write `bg-surface text-foreground` and never raw colors. Changing the palette means editing this one file.

| Token | Use |
|---|---|
| `background`, `surface`, `surface-raised` | Page, cards and panels, raised elements |
| `foreground`, `muted-foreground` | Main text, secondary text |
| `border`, `ring` | Borders, focus outline |
| `primary`, `primary-foreground` | Main action color and the text on it |
| `accent`, `accent-foreground` | Soft highlight (active entry) and the text on it |
| `success`, `warning`, `danger` | Status colors, used as text on `background` or `surface` |

Fonts are Inter (400, 500, 600, 700) and JetBrains Mono (400, 500), self-hosted through `@fontsource` and imported in `frontend/src/main.tsx`.

## Contrast

Every foreground and background pair of the tokens must reach at least 4.5:1 (WCAG AA for text) in both themes. Ratios of the current palette:

| Theme | Pair | Ratio |
|---|---|---|
| light | `foreground on background` | 16.97 |
| light | `foreground on surface` | 17.71 |
| light | `foreground on surface-raised` | 16.01 |
| light | `muted-foreground on background` | 7.12 |
| light | `muted-foreground on surface` | 7.43 |
| light | `muted-foreground on surface-raised` | 6.72 |
| light | `primary-foreground on primary` | 6.47 |
| light | `accent-foreground on accent` | 8.97 |
| light | `primary on background` | 6.38 |
| light | `primary on surface` | 6.66 |
| light | `success on background` | 6.74 |
| light | `success on surface` | 7.04 |
| light | `warning on background` | 5.89 |
| light | `warning on surface` | 6.15 |
| light | `danger on background` | 6.39 |
| light | `danger on surface` | 6.67 |
| dark | `foreground on background` | 17.02 |
| dark | `foreground on surface` | 15.77 |
| dark | `foreground on surface-raised` | 13.83 |
| dark | `muted-foreground on background` | 8.30 |
| dark | `muted-foreground on surface` | 7.69 |
| dark | `muted-foreground on surface-raised` | 6.74 |
| dark | `primary-foreground on primary` | 5.79 |
| dark | `accent-foreground on accent` | 10.74 |
| dark | `primary on background` | 5.63 |
| dark | `primary on surface` | 5.22 |
| dark | `success on background` | 10.11 |
| dark | `success on surface` | 9.37 |
| dark | `warning on background` | 10.81 |
| dark | `warning on surface` | 10.01 |
| dark | `danger on background` | 7.52 |
| dark | `danger on surface` | 6.97 |
