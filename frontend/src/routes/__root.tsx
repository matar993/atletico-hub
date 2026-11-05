import { createRootRoute, Outlet } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: () => (
    <main className="mx-auto min-h-screen max-w-3xl p-4">
      <Outlet />
    </main>
  ),
})
