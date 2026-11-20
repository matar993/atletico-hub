import { RouterProvider, createMemoryHistory, createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { fireEvent, render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { HomePage } from './HomePage'

async function renderHome() {
  const rootRoute = createRootRoute()
  const paths = ['/', '/events', '/call-ups', '/notifications']
  const routes = paths.map((path) =>
    createRoute({ getParentRoute: () => rootRoute, path, component: path === '/' ? HomePage : () => null }),
  )
  const router = createRouter({
    routeTree: rootRoute.addChildren(routes),
    history: createMemoryHistory({ initialEntries: ['/'] }),
  })
  await router.load()
  render(<RouterProvider router={router} />)
  return router
}

const PANELS = [
  { title: 'Prossimi eventi', path: '/events' },
  { title: 'Convocazioni', path: '/call-ups' },
  { title: 'Notifiche', path: '/notifications' },
]

describe('HomePage', () => {
  it('shows the Home heading and what the page is for', async () => {
    await renderHome()

    expect(screen.getByRole('heading', { level: 1, name: 'Home' })).toBeInTheDocument()
    expect(screen.getByText('Il riepilogo della squadra: prossimi eventi e novità.')).toBeInTheDocument()
  })

  it('shows the three panels', async () => {
    await renderHome()

    expect(screen.getAllByRole('heading', { level: 2 }).map((heading) => heading.textContent)).toEqual(
      PANELS.map(({ title }) => title),
    )
  })

  it('marks every panel as a preview', async () => {
    await renderHome()

    for (const { title } of PANELS) {
      const panel = screen.getByRole('heading', { name: title }).closest('section')!
      expect(within(panel).getByText('Anteprima')).toBeInTheDocument()
    }
  })

  it.each(PANELS)('leads to $path from the "$title" panel', async ({ title, path }) => {
    const router = await renderHome()

    fireEvent.click(screen.getByRole('link', { name: title }))

    expect(router.state.location.pathname).toBe(path)
  })
})
