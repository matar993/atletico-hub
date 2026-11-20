import { fireEvent, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn() } }))

const SECTIONS = ['/', '/events', '/call-ups', '/squad', '/notifications', '/profile']

describe('AppLayout', () => {
  beforeEach(() => {
    vi.mocked(api.GET).mockResolvedValue({
      data: { first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'player' },
      response: new Response(null, { status: 200 }),
    } as never)
  })

  it('shows the team name in the header', async () => {
    await renderApp('/')

    expect(screen.getByText('Atletico San Lorenzo')).toBeInTheDocument()
  })

  it('shows the page of the current route in the content area', async () => {
    await renderApp('/squad')

    expect(screen.getByRole('heading', { name: 'Rosa' })).toBeInTheDocument()
  })

  it.each(SECTIONS)('keeps the path %s of the section', async (path) => {
    const { router } = await renderApp(path)

    expect(router.state.location.pathname).toBe(path)
  })

  it('shows the name of the signed-in user in the header', async () => {
    await renderApp('/')

    expect(screen.getByText('Anna Rossi')).toBeInTheDocument()
  })

  it('logs out through the API and opens the login page', async () => {
    vi.mocked(api.POST).mockResolvedValue({ response: new Response(null, { status: 204 }) } as never)
    const { router } = await renderApp('/squad')
    vi.mocked(api.GET).mockResolvedValue({ error: {}, response: new Response(null, { status: 401 }) } as never)

    fireEvent.click(screen.getByRole('button', { name: 'Esci' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/login'))
    expect(api.POST).toHaveBeenCalledWith('/auth/logout')
  })
})
