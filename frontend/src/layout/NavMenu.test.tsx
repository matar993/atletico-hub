import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createMemoryHistory, createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CURRENT_USER_KEY } from '@/auth/currentUser'
import { NavMenu } from './NavMenu'
import { NAV_ENTRIES } from './navigation'

const SIX = ['Home', 'Eventi', 'Convocazioni', 'Rosa', 'Notifiche', 'Profilo']

async function renderMenuAt(path: string, role: 'admin' | 'player' = 'player') {
  const queryClient = new QueryClient()
  queryClient.setQueryData(CURRENT_USER_KEY, { first_name: 'Anna', last_name: 'Rossi', email: 'a@example.com', role })
  const rootRoute = createRootRoute({ component: NavMenu })
  const routes = NAV_ENTRIES.map(({ to }) => createRoute({ getParentRoute: () => rootRoute, path: to }))
  const router = createRouter({
    routeTree: rootRoute.addChildren(routes),
    history: createMemoryHistory({ initialEntries: [path] }),
  })
  await router.load()
  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
}

describe('NavMenu', () => {
  it('lists the six sections in order to a player, with no Utenti', async () => {
    await renderMenuAt('/')

    const labels = screen.getAllByRole('link').map((link) => link.textContent)
    expect(labels).toEqual(SIX)
  })

  it('lists the seven sections in order to an admin, Utenti last', async () => {
    await renderMenuAt('/', 'admin')

    const labels = screen.getAllByRole('link').map((link) => link.textContent)
    expect(labels).toEqual([...SIX, 'Utenti'])
  })

  it('marks only the current section as the current page', async () => {
    await renderMenuAt('/events')

    const current = screen.getAllByRole('link').filter((l) => l.getAttribute('aria-current') === 'page')
    expect(current).toHaveLength(1)
    expect(screen.getByRole('link', { name: 'Eventi' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('link', { name: 'Home' })).not.toHaveAttribute('aria-current')
  })
})
