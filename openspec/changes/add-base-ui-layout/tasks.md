# Tasks

## 1. Dependency

- [x] 1.1 Add `lucide-react` to `frontend/package.json` dependencies and update `package-lock.json` (`docker compose exec ui npm install lucide-react`); verify `make ui-build` passes

## 2. Section pages and routes

- [x] 2.1 Add `src/layout/PlaceholderPage.tsx` (heading, description line, empty state) with `PlaceholderPage.test.tsx`; verify `make ui-test` passes, querying by role and text
- [x] 2.2 Rewrite `src/home/HomePage.tsx` on `PlaceholderPage` and add `EventsPage`, `CallUpsPage`, `SquadPage`, `NotificationsPage`, `ProfilePage` in their feature folders, with the Italian texts of the spec; update `HomePage.test.tsx` to the "Home" heading; verify `make ui-test` passes
- [x] 2.3 Add the thin route files `events.tsx`, `call-ups.tsx`, `squad.tsx`, `notifications.tsx`, `profile.tsx` in `src/routes/` and regenerate `routeTree.gen.ts`; verify `make ui-typecheck` passes and each path renders its page in `npm run dev`

## 3. Layout and navigation

- [x] 3.1 Add `src/layout/navigation.ts` (team name constant, ordered entries `{ label, to, icon }` typed on the router paths) and `NavMenu.tsx` (router `Link`, active highlight, `exact` on Home) with `NavMenu.test.tsx` on a memory-history router: six entries in order, only the current one with `aria-current="page"`; verify `make ui-test` passes
- [x] 3.2 Add `src/layout/AppLayout.tsx` (header with team name, `md:` fixed sidebar, hamburger button and `<dialog>` drawer below `md`, content area with `<Outlet />`) and render it from `src/routes/__root.tsx`; add `AppLayout.test.tsx` for the team name and the routed content; verify `make ui-test` passes
- [ ] 3.3 Set `lang="it"` in `frontend/index.html`; verify the built `dist/index.html` carries it after `make ui-build`

## 4. Browser tests

- [ ] 4.1 Replace `e2e/home.spec.ts` with `e2e/navigation.spec.ts`: on a desktop viewport, the sidebar is visible, no hamburger button, every section is reachable from the menu and its entry is active; on a phone viewport, the menu is hidden, the drawer opens from the hamburger button, choosing "Rosa" navigates and closes it, Escape closes it without navigating; verify `make ui-e2e` passes

## 5. Documentation

- [ ] 5.1 Add the user guide page for the navigation (sections, sidebar on desktop, drawer on phone) under `docs/documents/user-guide/` and list it in its index; update "Today" in `ARCHITECTURE.md` (layout and placeholder sections); verify every link resolves and `make validate` passes

## 6. Integration check

- [ ] 6.1 Run `make ui-checks` and `make ui-e2e`; verify both pass on the final tree

## Workflow follow-up

- Archive the change with `/openspec-archive-change` in the implementation pull request.
