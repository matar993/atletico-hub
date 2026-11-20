import { useQueryClient } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { useState, type FormEvent } from 'react'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import { TEAM_NAME } from '@/layout/navigation'
import { BUTTON_PRIMARY, FIELD_INPUT, FIELD_LABEL, FORM_ERROR } from '@/ui/classes'
import { CURRENT_USER_KEY } from './currentUser'
import { safeRedirect } from './safeRedirect'

export function LoginPage({ redirect }: { redirect: string | undefined }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setSubmitting(true)
    setError(null)
    const { data, error: apiError } = await api.POST('/auth/login', {
      body: { email: String(form.get('email')), password: String(form.get('password')) },
    })
    setSubmitting(false)
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    queryClient.setQueryData(CURRENT_USER_KEY, data)
    router.history.push(safeRedirect(redirect))
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4 text-foreground">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-lg border border-border bg-surface p-6">
        <div className="space-y-1">
          <p className="text-xs font-semibold tracking-wider text-primary uppercase">{TEAM_NAME}</p>
          <h1 className="text-2xl font-bold tracking-tight">Accedi</h1>
        </div>
        {error && (
          <p role="alert" className={FORM_ERROR}>
            {error}
          </p>
        )}
        <label className={FIELD_LABEL}>
          Email
          <input name="email" type="email" autoComplete="email" required className={FIELD_INPUT} />
        </label>
        <label className={FIELD_LABEL}>
          Password
          <input name="password" type="password" autoComplete="current-password" required className={FIELD_INPUT} />
        </label>
        <button type="submit" disabled={submitting} className={`${BUTTON_PRIMARY} w-full`}>
          Accedi
        </button>
        <p className="text-sm text-muted-foreground">
          Sei un nuovo giocatore? Chiedi all&apos;admin il link per creare il tuo account.
        </p>
      </form>
    </main>
  )
}
