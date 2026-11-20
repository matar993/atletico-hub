import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { CURRENT_USER_KEY } from '@/auth/currentUser'
import { EmptyState } from '@/layout/EmptyState'
import { Page } from '@/layout/Page'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'
import { FIELD_INPUT, FORM_ERROR } from '@/ui/classes'
import { USERS_KEY, usersQuery } from './usersQuery'

type Account = components['schemas']['AccountSummary']
type Role = Account['role']

const ROLE_LABELS: Record<Role, string> = { admin: 'Admin', player: 'Giocatore' }

export function UsersPage() {
  const queryClient = useQueryClient()
  const users = useQuery(usersQuery)
  const [error, setError] = useState<string | null>(null)

  async function changeRole(account: Account, role: Role) {
    setError(null)
    const { data, error: apiError } = await api.PUT('/users/{account_id}/role', {
      params: { path: { account_id: account.id } },
      body: { role },
    })
    if (!data) {
      // The list is not touched: the select goes back to the role the API still has.
      setError(apiErrorMessage(apiError))
      return
    }
    // An admin can change their own role, and the menu follows the role of the current user.
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: USERS_KEY }),
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY }),
    ])
  }

  return (
    <Page eyebrow="Atletico Hub" title="Utenti" description="Gli account dell'app e i loro ruoli.">
      {users.isError && <p role="alert">Non riesco a caricare gli utenti. Riprova tra poco.</p>}
      {error && (
        <p role="alert" className={FORM_ERROR}>
          {error}
        </p>
      )}
      {users.data?.items.length === 0 && <EmptyState icon={ShieldCheck}>Nessun utente.</EmptyState>}
      {users.data && users.data.items.length > 0 && (
        <ul className="space-y-3">
          {users.data.items.map((account) => (
            <li
              key={account.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-surface p-4"
            >
              <div>
                <p className="font-medium">
                  {account.first_name} {account.last_name}
                </p>
                <p className="text-sm text-muted-foreground">{account.email}</p>
              </div>
              {account.permissions.change_role ? (
                <select
                  aria-label={`Ruolo di ${account.first_name} ${account.last_name}`}
                  value={account.role}
                  onChange={(event) => changeRole(account, event.target.value as Role)}
                  className={`${FIELD_INPUT} w-auto`}
                >
                  {(Object.keys(ROLE_LABELS) as Role[]).map((role) => (
                    <option key={role} value={role}>
                      {ROLE_LABELS[role]}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="text-sm font-medium">{ROLE_LABELS[account.role]}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </Page>
  )
}
