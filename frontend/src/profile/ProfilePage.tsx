import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { CURRENT_USER_KEY, currentUserQuery } from '@/auth/currentUser'
import { Page } from '@/layout/Page'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import { SQUAD_KEY } from '@/squad/squadQuery'
import { BUTTON_PRIMARY, FIELD_INPUT, FIELD_LABEL, FORM_ERROR } from '@/ui/classes'

const ROLE_LABELS = { admin: 'Admin', player: 'Giocatore' } as const

export function ProfilePage() {
  const queryClient = useQueryClient()
  const { data: user } = useQuery(currentUserQuery)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setSubmitting(true)
    setError(null)
    setSaved(false)
    const { data, error: apiError } = await api.PATCH('/profile', {
      body: { first_name: String(form.get('first_name')), last_name: String(form.get('last_name')) },
    })
    setSubmitting(false)
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY }),
      queryClient.invalidateQueries({ queryKey: SQUAD_KEY }),
    ])
    setSaved(true)
  }

  return (
    <Page eyebrow="Atletico Hub" title="Profilo" description="I tuoi dati personali.">
      {user && (
        <div className="max-w-md space-y-6">
          <dl className="space-y-3 rounded-lg border border-border bg-surface p-4 text-sm">
            <div>
              <dt className="text-muted-foreground">Email</dt>
              <dd className="font-medium">{user.email}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Ruolo</dt>
              <dd className="font-medium">{ROLE_LABELS[user.role]}</dd>
            </div>
          </dl>
          <form onSubmit={submit} className="space-y-4">
            {error && (
              <p role="alert" className={FORM_ERROR}>
                {error}
              </p>
            )}
            <label className={FIELD_LABEL}>
              Nome
              <input name="first_name" required maxLength={50} defaultValue={user.first_name} className={FIELD_INPUT} />
            </label>
            <label className={FIELD_LABEL}>
              Cognome
              <input name="last_name" required maxLength={50} defaultValue={user.last_name} className={FIELD_INPUT} />
            </label>
            <div className="flex items-center gap-3">
              <button type="submit" disabled={submitting} className={BUTTON_PRIMARY}>
                Salva
              </button>
              {saved && <p role="status">Profilo aggiornato</p>}
            </div>
          </form>
        </div>
      )}
    </Page>
  )
}
