import { fireEvent, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn() } }))

const USER = { first_name: 'Luca', last_name: 'Bianchi', email: 'luca@example.com', role: 'player' }
const INVALID = "Link non valido o scaduto. Chiedi un nuovo link all'admin."

function inviteAnswer(invite: object | null) {
  vi.mocked(api.GET).mockImplementation((async (path: string) => {
    if (path === '/auth/invites/{token}') {
      return invite === null
        ? { error: { detail: 'Link non valido o scaduto' }, response: new Response(null, { status: 404 }) }
        : { data: invite, response: new Response(null, { status: 200 }) }
    }
    return { data: USER, response: new Response(null, { status: 200 }) }
  }) as never)
}

describe('InvitePage', () => {
  beforeEach(() => {
    vi.mocked(api.POST).mockResolvedValue({ data: USER, response: new Response(null, { status: 200 }) } as never)
  })

  it('shows the invalid link message when the API answers 404', async () => {
    inviteAnswer(null)
    await renderApp('/invite/bad-token')

    expect(await screen.findByText(INVALID)).toBeInTheDocument()
  })

  it('asks a player without an account for an email and a password, and creates the account', async () => {
    inviteAnswer({ first_name: 'Luca', last_name: 'Bianchi', has_account: false, email: null })
    const { router } = await renderApp('/invite/tok')

    expect(await screen.findByRole('heading', { name: 'Ciao Luca Bianchi' })).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'luca@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret-pass' } })
    fireEvent.click(screen.getByRole('button', { name: 'Crea account' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/'))
    expect(api.POST).toHaveBeenCalledWith('/auth/invites/{token}/accept', {
      params: { path: { token: 'tok' } },
      body: { email: 'luca@example.com', password: 'secret-pass' },
    })
  })

  it('shows the email of a player with an account and asks only for a new password', async () => {
    inviteAnswer({ first_name: 'Luca', last_name: 'Bianchi', has_account: true, email: 'luca@example.com' })
    const { router } = await renderApp('/invite/tok')

    expect(await screen.findByText('luca@example.com')).toBeInTheDocument()
    expect(screen.queryByLabelText('Email')).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Nuova password'), { target: { value: 'new-secret-pass' } })
    fireEvent.click(screen.getByRole('button', { name: 'Imposta la password' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/'))
    expect(api.POST).toHaveBeenCalledWith('/auth/invites/{token}/accept', {
      params: { path: { token: 'tok' } },
      body: { email: null, password: 'new-secret-pass' },
    })
  })

  it('shows the error of the API when the email is in use and stays on the page', async () => {
    inviteAnswer({ first_name: 'Luca', last_name: 'Bianchi', has_account: false, email: null })
    vi.mocked(api.POST).mockResolvedValue({
      error: { detail: 'Email già in uso' },
      response: new Response(null, { status: 409 }),
    } as never)
    const { router } = await renderApp('/invite/tok')

    await screen.findByRole('heading', { name: 'Ciao Luca Bianchi' })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'anna@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret-pass' } })
    fireEvent.click(screen.getByRole('button', { name: 'Crea account' }))

    expect(await screen.findByText('Email già in uso')).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/invite/tok')
  })
})
