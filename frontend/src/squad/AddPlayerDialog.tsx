import * as Dialog from '@radix-ui/react-dialog'
import { useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import { BUTTON_PRIMARY, BUTTON_SECONDARY, FIELD_INPUT, FIELD_LABEL, FORM_ERROR } from '@/ui/classes'
import { SQUAD_KEY } from './squadQuery'

export function AddPlayerDialog() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function onOpenChange(next: boolean) {
    setOpen(next)
    setError(null)
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setSubmitting(true)
    setError(null)
    const { data, error: apiError } = await api.POST('/players', {
      body: { first_name: String(form.get('first_name')), last_name: String(form.get('last_name')) },
    })
    setSubmitting(false)
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    await queryClient.invalidateQueries({ queryKey: SQUAD_KEY })
    setOpen(false)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Trigger className={BUTTON_PRIMARY}>Aggiungi giocatore</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-lg border border-border bg-surface p-6 shadow-soft"
        >
          <form onSubmit={submit} className="space-y-4">
            <Dialog.Title className="text-lg font-semibold">Aggiungi giocatore</Dialog.Title>
            {error && (
              <p role="alert" className={FORM_ERROR}>
                {error}
              </p>
            )}
            <label className={FIELD_LABEL}>
              Nome
              <input name="first_name" required maxLength={50} className={FIELD_INPUT} />
            </label>
            <label className={FIELD_LABEL}>
              Cognome
              <input name="last_name" required maxLength={50} className={FIELD_INPUT} />
            </label>
            <div className="flex justify-end gap-2">
              <Dialog.Close className={BUTTON_SECONDARY}>Annulla</Dialog.Close>
              <button type="submit" disabled={submitting} className={BUTTON_PRIMARY}>
                Aggiungi
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
