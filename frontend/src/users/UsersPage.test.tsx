import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn(), PATCH: vi.fn(), PUT: vi.fn() } }))

const OK = () => new Response(null, { status: 200 })

let accounts: { id: number; first_name: string; last_name: string; email: string; role: 'admin' | 'player' }[]

beforeEach(() => {
  accounts = [
    { id: 1, first_name: 'Luca', last_name: 'Bianchi', email: 'luca@example.com', role: 'player' },
    { id: 2, first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'admin' },
  ]
  vi.mocked(api.GET).mockImplementation((async (path: string) =>
    path === '/auth/me'
      ? { data: { first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'admin' }, response: OK() }
      : {
          data: { items: accounts.map((a) => ({ ...a, permissions: { change_role: true } })) },
          response: OK(),
        }) as never)
})

describe('UsersPage', () => {
  it('lists every account with name, email and role', async () => {
    await renderApp('/users')

    expect(await screen.findByText('Luca Bianchi')).toBeInTheDocument()
    expect(screen.getByText('luca@example.com')).toBeInTheDocument()
    expect(screen.getByLabelText('Ruolo di Luca Bianchi')).toHaveValue('player')
    expect(screen.getByLabelText('Ruolo di Anna Rossi')).toHaveValue('admin')
  })

  it('shows the role as text when the flag does not allow the change', async () => {
    vi.mocked(api.GET).mockImplementation((async (path: string) =>
      path === '/auth/me'
        ? { data: { first_name: 'A', last_name: 'B', email: 'a@b.it', role: 'admin' }, response: OK() }
        : { data: { items: [{ ...accounts[0], permissions: { change_role: false } }] }, response: OK() }) as never)
    await renderApp('/users')

    expect(await screen.findByText('Giocatore')).toBeInTheDocument()
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
  })

  it('changes a role through PUT and shows the new role after the reload', async () => {
    vi.mocked(api.PUT).mockImplementation((async () => {
      accounts = accounts.map((a) => (a.id === 1 ? { ...a, role: 'admin' as const } : a))
      return { data: { id: 1, role: 'admin' }, response: OK() }
    }) as never)
    await renderApp('/users')
    const select = await screen.findByLabelText('Ruolo di Luca Bianchi')

    fireEvent.change(select, { target: { value: 'admin' } })

    expect(api.PUT).toHaveBeenCalledWith('/users/{account_id}/role', {
      params: { path: { account_id: 1 } },
      body: { role: 'admin' },
    })
    await waitFor(() => expect(screen.getByLabelText('Ruolo di Luca Bianchi')).toHaveValue('admin'))
  })

  it('shows the message of the API when the last admin is refused and keeps the old role', async () => {
    vi.mocked(api.PUT).mockResolvedValue({
      error: { detail: 'Serve almeno un admin' },
      response: new Response(null, { status: 409 }),
    } as never)
    await renderApp('/users')
    const select = await screen.findByLabelText('Ruolo di Anna Rossi')

    fireEvent.change(select, { target: { value: 'player' } })

    expect(await screen.findByText('Serve almeno un admin')).toBeInTheDocument()
    expect(screen.getByLabelText('Ruolo di Anna Rossi')).toHaveValue('admin')
    expect(within(screen.getByRole('alert')).getByText('Serve almeno un admin')).toBeInTheDocument()
  })
})
