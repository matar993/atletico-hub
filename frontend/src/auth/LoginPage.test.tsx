import { fireEvent, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn() } }))

const USER = { first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'player' }

async function submitLogin() {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'anna@example.com' } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret-pass' } })
  fireEvent.click(screen.getByRole('button', { name: 'Accedi' }))
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.mocked(api.GET).mockResolvedValue({ error: {}, response: new Response(null, { status: 401 }) } as never)
  })

  it('says that a new player gets access through a link from the admin', async () => {
    await renderApp('/login')

    expect(screen.getByText(/Chiedi all'admin il link/)).toBeInTheDocument()
  })

  it('shows the message of the API on a failed login and stays on the page', async () => {
    vi.mocked(api.POST).mockResolvedValue({
      error: { detail: 'Email o password non corretti' },
      response: new Response(null, { status: 401 }),
    } as never)
    const { router } = await renderApp('/login')

    await submitLogin()

    expect(await screen.findByText('Email o password non corretti')).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')
  })

  it('opens the requested section after a successful login', async () => {
    vi.mocked(api.POST).mockResolvedValue({ data: USER, response: new Response(null, { status: 200 }) } as never)
    const { router } = await renderApp('/login?redirect=%2Fsquad')

    await submitLogin()

    await waitFor(() => expect(router.state.location.pathname).toBe('/squad'))
    expect(await screen.findByRole('heading', { name: 'Rosa' })).toBeInTheDocument()
  })

  it('opens Home when the redirect points to another site', async () => {
    vi.mocked(api.POST).mockResolvedValue({ data: USER, response: new Response(null, { status: 200 }) } as never)
    const { router } = await renderApp('/login?redirect=https%3A%2F%2Fevil.example')

    await submitLogin()

    await waitFor(() => expect(router.state.location.pathname).toBe('/'))
  })
})
