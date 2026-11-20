import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { useState, type FormEvent } from 'react'
import { CURRENT_USER_KEY } from '@/auth/currentUser'
import { TEAM_NAME } from '@/layout/navigation'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import { BUTTON_PRIMARY, FIELD_INPUT, FIELD_LABEL, FORM_ERROR } from '@/ui/classes'

export const INVALID_INVITE_MESSAGE = "Link non valido o scaduto. Chiedi un nuovo link all'admin."

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4 text-foreground">
      <div className="w-full max-w-sm space-y-4 rounded-lg border border-border bg-surface p-6">
        <p className="text-xs font-semibold tracking-wider text-primary uppercase">{TEAM_NAME}</p>
        {children}
      </div>
    </main>
  )
}

export function InvitePage({ token }: { token: string }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const invite = useQuery({
    queryKey: ['invite', token],
    retry: false,
    queryFn: async () => {
      const { data, response } = await api.GET('/auth/invites/{token}', { params: { path: { token } } })
      if (response.status === 404) return null
      if (!data) throw new Error(`Invite: unexpected status ${response.status}`)
      return data
    },
  })

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const email = form.get('email')
    setSubmitting(true)
    setError(null)
    const { data, error: apiError } = await api.POST('/auth/invites/{token}/accept', {
      params: { path: { token } },
      body: { email: email === null ? null : String(email), password: String(form.get('password')) },
    })
    setSubmitting(false)
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    queryClient.setQueryData(CURRENT_USER_KEY, data)
    await router.navigate({ to: '/' })
  }

  if (invite.isPending) {
    return (
      <Shell>
        <p>Caricamento…</p>
      </Shell>
    )
  }
  if (invite.isError || invite.data === null) {
    return (
      <Shell>
        <p role="alert">{INVALID_INVITE_MESSAGE}</p>
      </Shell>
    )
  }

  const { first_name, last_name, email } = invite.data
  const hasAccount = invite.data.has_account
  return (
    <Shell>
      <form onSubmit={submit} className="space-y-4">
        <h1 className="text-2xl font-bold tracking-tight">
          Ciao {first_name} {last_name}
        </h1>
        <p className="text-sm text-muted-foreground">
          {hasAccount ? 'Scegli una nuova password per il tuo account.' : 'Crea il tuo account con email e password.'}
        </p>
        {error && (
          <p role="alert" className={FORM_ERROR}>
            {error}
          </p>
        )}
        {hasAccount ? (
          <p className="text-sm">
            Email: <strong>{email}</strong>
          </p>
        ) : (
          <label className={FIELD_LABEL}>
            Email
            <input name="email" type="email" autoComplete="email" required className={FIELD_INPUT} />
          </label>
        )}
        <label className={FIELD_LABEL}>
          {hasAccount ? 'Nuova password' : 'Password'}
          <input
            name="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={128}
            className={FIELD_INPUT}
          />
        </label>
        <button type="submit" disabled={submitting} className={`${BUTTON_PRIMARY} w-full`}>
          {hasAccount ? 'Imposta la password' : 'Crea account'}
        </button>
      </form>
    </Shell>
  )
}
