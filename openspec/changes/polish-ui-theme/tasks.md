## 1. Dependencies and tokens

- [x] 1.1 Add `framer-motion`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@fontsource/inter`, `@fontsource/jetbrains-mono`, `tailwind-merge`, `clsx` to `frontend/package.json` and update the lock file (`docker compose exec ui npm install ...`); verify `make ui-build` passes and note the bundle size
- [x] 1.2 Add `src/lib/cn.ts` with `cn.test.ts` (merges conflicting Tailwind classes, drops falsy values); verify `make ui-test` passes
- [x] 1.3 Define OKLCH tokens (light and `.dark`), `@theme inline` mapping, base styles and font imports in `src/styles/globals.css` and `src/main.tsx`; verify `make ui-build` passes and the built CSS and fonts load from `'self'` in `npm run dev`
- [x] 1.4 Check the contrast of every foreground/background token pair in both themes is at least 4.5:1; record the pairs and ratios in the developer guide token section; verify by script output in the task commit message

## 2. Theme

- [x] 2.1 Add `public/theme-init.js` and load it in the `<head>` of `index.html` before the CSS; verify the built `dist/index.html` references it and `.dark` is set before first paint in `npm run dev`
- [x] 2.2 Add `src/theme/` (`ThemeProvider`, `useTheme`) with unit tests: default system, saved choice, system change event, storage that throws; verify `make ui-test` passes
- [x] 2.3 Add `ThemeMenu` (Radix DropdownMenu, radio items Chiaro, Scuro, Sistema, accessible name "Tema") with unit tests selecting each choice and checking `.dark` on `<html>`; verify `make ui-test` passes

## 3. Shell

- [x] 3.1 Restyle `NavMenu` with tokens and the animated active marker (`framer-motion`, `layoutId` per container, reduced motion respected); verify the existing `NavMenu.test.tsx` passes unchanged
- [ ] 3.2 Rebuild `AppLayout`: sticky header with brand mark, team name and `ThemeMenu`; restyled fixed sidebar; Radix Dialog drawer with slide animation; keep names `Menu principale`, `Apri il menu`, `Chiudi il menu`; verify the existing `AppLayout.test.tsx` and `e2e/navigation.spec.ts` pass unchanged
- [ ] 3.3 Add unit tests for the drawer in jsdom: open, choose entry closes it, Escape closes it, close button closes it, hamburger `aria-expanded`; verify `make ui-test` passes

## 4. Pages

- [ ] 4.1 Add `Page` and `EmptyState` in `src/layout/` with tests (one `h1`, eyebrow, description, actions, empty state text); rewrite `PlaceholderPage` on them keeping its props; verify the existing `PlaceholderPage.test.tsx` passes unchanged
- [ ] 4.2 Add `Panel` and the sample content constant in `src/home/`; rebuild `HomePage` with three panels, `Anteprima` badges and links to sections; update `HomePage.test.tsx` (three panels, badges, link targets); verify `make ui-test` passes

## 5. Browser tests

- [ ] 5.1 Add `e2e/theme.spec.ts`: choosing Scuro survives a reload with `.dark` set right after navigation, Sistema follows `colorScheme` emulation, keyboard-only use of the theme menu; verify `make ui-e2e` passes
- [ ] 5.2 Extend the phone drawer spec for reduced motion (`reducedMotion: 'reduce'`) and run the full suite on the production image; verify `make ui-e2e` passes with no CSP violation in the console

## 6. Documentation and final checks

- [ ] 6.1 Update `docs/documents/user-guide/navigation.md` (theme control, Home panels), add a design tokens and "add a component" section to the developer guide, update `ARCHITECTURE.md` "Today"; verify links resolve
- [ ] 6.2 Run `make ui-checks` and `make ui-e2e` on the final tree; verify both pass, then capture light and dark screenshots of Home on phone and desktop for review

## Workflow follow-up

- Archive `add-base-ui-layout` first, then this change, in the implementation pull request (`/openspec-archive-change`).
- Ask the user for the official club colors and update the tokens if they differ.
