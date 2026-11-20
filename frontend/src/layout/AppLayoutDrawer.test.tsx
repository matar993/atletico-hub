import { RouterProvider, createMemoryHistory, createRouter } from '@tanstack/react-router'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { routeTree } from '@/routeTree.gen'

async function renderAt(path: string) {
  const router = createRouter({
    routeTree,
    history: createMemoryHistory({ initialEntries: [path] }),
  })
  await router.load()
  render(<RouterProvider router={router} />)
  return router
}

const hamburger = () => screen.getByRole('button', { name: 'Apri il menu', hidden: true })

async function openDrawer() {
  fireEvent.click(hamburger())
  return screen.findByRole('dialog')
}

describe('AppLayout drawer', () => {
  it('is closed at first and the hamburger button says so', async () => {
    await renderAt('/')

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(hamburger()).toHaveAttribute('aria-expanded', 'false')
  })

  it('opens from the hamburger button with the menu inside', async () => {
    await renderAt('/')

    const drawer = await openDrawer()

    expect(hamburger()).toHaveAttribute('aria-expanded', 'true')
    expect(within(drawer).getByRole('navigation', { name: 'Menu principale' })).toBeInTheDocument()
  })

  it('closes and navigates when an entry is chosen', async () => {
    const router = await renderAt('/')
    const drawer = await openDrawer()

    fireEvent.click(within(drawer).getByRole('link', { name: 'Rosa' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(router.state.location.pathname).toBe('/squad')
    expect(hamburger()).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes with Escape without navigating', async () => {
    const router = await renderAt('/events')
    const drawer = await openDrawer()

    fireEvent.keyDown(drawer, { key: 'Escape' })

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(router.state.location.pathname).toBe('/events')
  })

  it('closes with the close button', async () => {
    await renderAt('/')
    const drawer = await openDrawer()

    fireEvent.click(within(drawer).getByRole('button', { name: 'Chiudi il menu' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })
})
