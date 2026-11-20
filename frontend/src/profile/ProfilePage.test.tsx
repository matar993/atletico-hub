import { fireEvent, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn(), PATCH: vi.fn() } }))

const OK = () => new Response(null, { status: 200 })

let me = { first_name: 'Marco', last_name: 'Rossi', email: 'marco@example.com', role: 'player' }

beforeEach(() => {
  me = { first_name: 'Marco', last_name: 'Rossi', email: 'marco@example.com', role: 'player' }
  vi.mocked(api.GET).mockImplementation((async (path: string) =>
    path === '/auth/me'
      ? { data: me, response: OK() }
      : { data: { permissions: { create: false }, items: [] }, response: OK() }) as never)
})

describe('ProfilePage', () => {
  it('shows the name, the email and the role of the current user', async () => {
    await renderApp('/profile')

    expect(await screen.findByLabelText('Nome')).toHaveValue('Marco')
    expect(screen.getByLabelText('Cognome')).toHaveValue('Rossi')
    expect(screen.getByText('marco@example.com')).toBeInTheDocument()
    expect(screen.getByText('Giocatore')).toBeInTheDocument()
  })

  it('shows the role of an admin', async () => {
    me = { ...me, role: 'admin' }
    await renderApp('/profile')

    expect(await screen.findByText('Admin')).toBeInTheDocument()
  })

  it('saves the new name through PATCH /profile and the header shows it', async () => {
    vi.mocked(api.PATCH).mockImplementation((async () => {
      me = { ...me, last_name: 'Bianchi Rossi' }
      return { data: me, response: OK() }
    }) as never)
    await renderApp('/profile')
    fireEvent.change(await screen.findByLabelText('Cognome'), { target: { value: 'Bianchi Rossi' } })

    fireEvent.click(screen.getByRole('button', { name: 'Salva' }))

    expect(await screen.findByText('Profilo aggiornato')).toBeInTheDocument()
    expect(api.PATCH).toHaveBeenCalledWith('/profile', { body: { first_name: 'Marco', last_name: 'Bianchi Rossi' } })
    await waitFor(() => expect(screen.getByText('Marco Bianchi Rossi')).toBeInTheDocument())
  })

  it('shows the message of the API when the name is refused and keeps the form', async () => {
    vi.mocked(api.PATCH).mockResolvedValue({
      error: { detail: 'A name needs 1 to 50 characters, got 0' },
      response: new Response(null, { status: 422 }),
    } as never)
    await renderApp('/profile')
    fireEvent.change(await screen.findByLabelText('Nome'), { target: { value: ' ' } })

    fireEvent.click(screen.getByRole('button', { name: 'Salva' }))

    expect(await screen.findByText('A name needs 1 to 50 characters, got 0')).toBeInTheDocument()
    expect(screen.queryByText('Profilo aggiornato')).not.toBeInTheDocument()
  })
})
