import { screen } from '@testing-library/react'
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
})
