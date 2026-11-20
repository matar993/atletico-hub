import * as Dialog from '@radix-ui/react-dialog'
import { useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { CURRENT_USER_KEY } from '@/auth/currentUser'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'
import { BUTTON_PRIMARY, BUTTON_SECONDARY, FIELD_INPUT, FIELD_LABEL, FORM_ERROR } from '@/ui/classes'
import { SQUAD_KEY } from './squadQuery'

type Member = components['schemas']['SquadMember']

export function RenamePlayerDialog({ member }: { member: Member }) {
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
    const { data, error: apiError } = await api.PATCH('/players/{player_id}', {
      params: { path: { player_id: member.id } },
      body: { first_name: String(form.get('first_name')), last_name: String(form.get('last_name')) },
    })
    setSubmitting(false)
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    // The renamed player can be the signed-in admin: the header shows the name of the current user.
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: SQUAD_KEY }),
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY }),
    ])
    setOpen(false)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Trigger className={BUTTON_SECONDARY}>Modifica nome</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-lg border border-border bg-surface p-6 shadow-soft"
        >
          <form onSubmit={submit} className="space-y-4">
            <Dialog.Title className="text-lg font-semibold">Modifica nome</Dialog.Title>
            {error && (
              <p role="alert" className={FORM_ERROR}>
                {error}
              </p>
            )}
            <label className={FIELD_LABEL}>
              Nome
              <input
                name="first_name"
                required
                maxLength={50}
                defaultValue={member.first_name}
                className={FIELD_INPUT}
              />
            </label>
            <label className={FIELD_LABEL}>
              Cognome
              <input name="last_name" required maxLength={50} defaultValue={member.last_name} className={FIELD_INPUT} />
            </label>
            <div className="flex justify-end gap-2">
              <Dialog.Close className={BUTTON_SECONDARY}>Annulla</Dialog.Close>
              <button type="submit" disabled={submitting} className={BUTTON_PRIMARY}>
                Salva
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
