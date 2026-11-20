import { Copy } from 'lucide-react'
import { useState } from 'react'
import { api } from '@/lib/api/client'
import { apiErrorMessage } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'
import { BUTTON_SECONDARY, FORM_ERROR } from '@/ui/classes'

type Member = components['schemas']['SquadMember']

type Invite = { link: string; expiresAt: string }

export function PlayerRow({ member, isAdmin }: { member: Member; isAdmin: boolean }) {
  const [invite, setInvite] = useState<Invite | null>(null)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function createInvite() {
    setError(null)
    setCopied(false)
    const { data, error: apiError } = await api.POST('/auth/invites', { body: { player_id: member.id } })
    if (!data) {
      setError(apiErrorMessage(apiError))
      return
    }
    setInvite({ link: `${window.location.origin}${data.path}`, expiresAt: data.expires_at })
  }

  async function copy(link: string) {
    await navigator.clipboard.writeText(link)
    setCopied(true)
  }

  return (
    <li className="space-y-3 rounded-lg border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-medium">
            {member.first_name} {member.last_name}
          </p>
          <p className="text-sm text-muted-foreground">
            {member.has_account ? 'Ha un account' : 'Senza account'}
            {isAdmin && member.email && ` · ${member.email}`}
          </p>
        </div>
        {isAdmin && (
          <button type="button" onClick={createInvite} className={BUTTON_SECONDARY}>
            Crea link d&apos;invito
          </button>
        )}
      </div>
      {error && (
        <p role="alert" className={FORM_ERROR}>
          {error}
        </p>
      )}
      {invite && (
        <div className="space-y-2 rounded-md bg-background p-3 text-sm">
          <div className="flex items-center gap-2">
            <input
              readOnly
              aria-label={`Link d'invito per ${member.first_name} ${member.last_name}`}
              value={invite.link}
              className="min-w-0 flex-1 rounded-md border border-border bg-surface px-2 py-1 font-mono text-xs"
            />
            <button type="button" onClick={() => copy(invite.link)} className={BUTTON_SECONDARY}>
              <Copy aria-hidden="true" className="mr-1 size-4" />
              Copia
            </button>
          </div>
          <p className="text-muted-foreground">
            Scade il {new Date(invite.expiresAt).toLocaleDateString('it-IT')}. Il link viene mostrato una sola volta:
            copialo ora.
          </p>
          {copied && <p role="status">Link copiato</p>}
        </div>
      )}
    </li>
  )
}
