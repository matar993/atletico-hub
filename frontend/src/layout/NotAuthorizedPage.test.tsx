import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn(), PATCH: vi.fn(), PUT: vi.fn() } }))

const OK = () => new Response(null, { status: 200 })

function signInAs(role: 'admin' | 'player') {
  vi.mocked(api.GET).mockImplementation((async (path: string) =>
    path === '/auth/me'
      ? { data: { first_name: 'Me', last_name: 'Self', email: 'me@example.com', role }, response: OK() }
      : { data: { items: [] }, response: OK() }) as never)
}

describe('NotAuthorizedPage', () => {
  it('shows a player who opens /users the page with a link to Home, inside the layout, and makes no call to /users', async () => {
    signInAs('player')
    await renderApp('/users')

    expect(await screen.findByText('Non hai i permessi per vedere questa pagina')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Torna alla Home' })).toHaveAttribute('href', '/')
    expect(screen.getByRole('navigation', { name: 'Menu principale' })).toBeInTheDocument()
    expect((vi.mocked(api.GET).mock.calls as unknown as [string][]).map(([path]) => path)).not.toContain('/users')
  })

  it('does not show the page to an admin on /users', async () => {
    signInAs('admin')
    await renderApp('/users')

    expect(await screen.findByRole('heading', { name: 'Utenti' })).toBeInTheDocument()
    expect(screen.queryByText('Non hai i permessi per vedere questa pagina')).not.toBeInTheDocument()
  })

  it('is what /forbidden shows, the place the app goes after a 403', async () => {
    signInAs('player')
    await renderApp('/forbidden')

    expect(await screen.findByText('Non hai i permessi per vedere questa pagina')).toBeInTheDocument()
  })
})
