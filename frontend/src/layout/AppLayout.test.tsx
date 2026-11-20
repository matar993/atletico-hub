import { RouterProvider, createMemoryHistory, createRouter } from '@tanstack/react-router'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { routeTree } from '@/routeTree.gen'

async function renderAt(path: string) {
  const router = createRouter({
    routeTree,
    history: createMemoryHistory({ initialEntries: [path] }),
  })
  await router.load()
  render(<RouterProvider router={router} />)
}

describe('AppLayout', () => {
  it('shows the team name in the header', async () => {
    await renderAt('/')

    expect(screen.getByText('Atletico San Lorenzo')).toBeInTheDocument()
  })

  it('shows the page of the current route in the content area', async () => {
    await renderAt('/squad')

    expect(screen.getByRole('heading', { name: 'Rosa' })).toBeInTheDocument()
  })
})
