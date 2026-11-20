import { RouterProvider, createMemoryHistory, createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { NavMenu } from './NavMenu'
import { NAV_ENTRIES } from './navigation'

async function renderMenuAt(path: string) {
  const rootRoute = createRootRoute({ component: NavMenu })
  const routes = NAV_ENTRIES.map(({ to }) => createRoute({ getParentRoute: () => rootRoute, path: to }))
  const router = createRouter({
    routeTree: rootRoute.addChildren(routes),
    history: createMemoryHistory({ initialEntries: [path] }),
  })
  await router.load()
  render(<RouterProvider router={router} />)
}

describe('NavMenu', () => {
  it('lists the six sections in order', async () => {
    await renderMenuAt('/')

    const labels = screen.getAllByRole('link').map((link) => link.textContent)
    expect(labels).toEqual(['Home', 'Eventi', 'Convocazioni', 'Rosa', 'Notifiche', 'Profilo'])
  })

  it('marks only the current section as the current page', async () => {
    await renderMenuAt('/events')

    const current = screen.getAllByRole('link').filter((l) => l.getAttribute('aria-current') === 'page')
    expect(current).toHaveLength(1)
    expect(screen.getByRole('link', { name: 'Eventi' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('link', { name: 'Home' })).not.toHaveAttribute('aria-current')
  })
})
