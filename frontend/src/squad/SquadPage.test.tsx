import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn() } }))

const OK = () => new Response(null, { status: 200 })
const SQUAD = [
  { id: 1, first_name: 'Anna', last_name: 'Rossi', has_account: true, email: 'anna@example.com' },
  { id: 2, first_name: 'Luca', last_name: 'Bianchi', has_account: false, email: null },
]

function signInAs(role: 'admin' | 'player', squad: object[] = SQUAD) {
  vi.mocked(api.GET).mockImplementation((async (path: string) =>
    path === '/auth/me'
      ? { data: { first_name: 'Me', last_name: 'Self', email: 'me@example.com', role }, response: OK() }
      : {
          data: squad.map((member) => (role === 'admin' ? member : { ...member, email: null })),
          response: OK(),
        }) as never)
}

describe('SquadPage', () => {
  describe('as a player', () => {
    beforeEach(() => signInAs('player'))

    it('lists the players with no email and no admin action', async () => {
      await renderApp('/squad')

      expect(await screen.findByText('Anna Rossi')).toBeInTheDocument()
      expect(screen.getByText('Luca Bianchi')).toBeInTheDocument()
      expect(screen.queryByText(/anna@example.com/)).not.toBeInTheDocument()
      expect(screen.queryByRole('button', { name: 'Aggiungi giocatore' })).not.toBeInTheDocument()
      expect(screen.queryByRole('button', { name: "Crea link d'invito" })).not.toBeInTheDocument()
    })

    it('says whether each player has an account', async () => {
      await renderApp('/squad')

      await screen.findByText('Anna Rossi')
      expect(screen.getByText('Ha un account')).toBeInTheDocument()
      expect(screen.getByText('Senza account')).toBeInTheDocument()
    })

    it('shows an empty state for an empty squad', async () => {
      signInAs('player', [])
      await renderApp('/squad')

      expect(await screen.findByText('Nessun giocatore in rosa.')).toBeInTheDocument()
    })
  })

  describe('as an admin', () => {
    beforeEach(() => signInAs('admin'))

    it('shows the email, the add button and an invite button per player', async () => {
      await renderApp('/squad')

      expect(await screen.findByText(/anna@example.com/)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Aggiungi giocatore' })).toBeInTheDocument()
      expect(screen.getAllByRole('button', { name: "Crea link d'invito" })).toHaveLength(2)
    })

    it('adds a player and reloads the list', async () => {
      vi.mocked(api.POST).mockResolvedValue({ data: { id: 3 }, response: OK() } as never)
      await renderApp('/squad')
      await screen.findByText('Anna Rossi')

      fireEvent.click(screen.getByRole('button', { name: 'Aggiungi giocatore' }))
      const dialog = await screen.findByRole('dialog')
      fireEvent.change(within(dialog).getByLabelText('Nome'), { target: { value: 'Marco' } })
      fireEvent.change(within(dialog).getByLabelText('Cognome'), { target: { value: 'Verdi' } })
      fireEvent.click(within(dialog).getByRole('button', { name: 'Aggiungi' }))

      await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
      expect(api.POST).toHaveBeenCalledWith('/players', { body: { first_name: 'Marco', last_name: 'Verdi' } })
      expect(
        (vi.mocked(api.GET).mock.calls as unknown as [string][]).filter(([path]) => path === '/players'),
      ).toHaveLength(2)
    })

    it('shows the error of the API when a player is refused', async () => {
      vi.mocked(api.POST).mockResolvedValue({
        error: { detail: 'A name needs 1 to 50 characters, got 0' },
        response: new Response(null, { status: 422 }),
      } as never)
      await renderApp('/squad')
      await screen.findByText('Anna Rossi')

      fireEvent.click(screen.getByRole('button', { name: 'Aggiungi giocatore' }))
      const dialog = await screen.findByRole('dialog')
      fireEvent.change(within(dialog).getByLabelText('Nome'), { target: { value: ' ' } })
      fireEvent.change(within(dialog).getByLabelText('Cognome'), { target: { value: 'Verdi' } })
      fireEvent.click(within(dialog).getByRole('button', { name: 'Aggiungi' }))

      expect(await within(dialog).findByText('A name needs 1 to 50 characters, got 0')).toBeInTheDocument()
    })

    it('creates an invite link, shows it once with its warning and copies it', async () => {
      const writeText = vi.fn().mockResolvedValue(undefined)
      Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
      vi.mocked(api.POST).mockResolvedValue({
        data: { path: '/invite/abc123', expires_at: '2026-12-01T10:00:00Z' },
        response: OK(),
      } as never)
      await renderApp('/squad')
      await screen.findByText('Luca Bianchi')

      fireEvent.click(screen.getAllByRole('button', { name: "Crea link d'invito" }).at(0) as HTMLElement)
      const field = await screen.findByLabelText(/Link d'invito per/)
      fireEvent.click(screen.getByRole('button', { name: /Copia/ }))

      expect(api.POST).toHaveBeenCalledWith('/auth/invites', { body: { player_id: expect.any(Number) } })
      expect(screen.getByText(/mostrato una sola volta/)).toBeInTheDocument()
      const link = (field as HTMLInputElement).value
      expect(link.endsWith('/invite/abc123')).toBe(true)
      await waitFor(() => expect(writeText).toHaveBeenCalledWith(link))
      expect(await screen.findByText('Link copiato')).toBeInTheDocument()
    })
  })
})
