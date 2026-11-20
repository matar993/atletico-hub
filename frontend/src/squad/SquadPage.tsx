import { useQuery } from '@tanstack/react-query'
import { Users } from 'lucide-react'
import { currentUserQuery } from '@/auth/currentUser'
import { EmptyState } from '@/layout/EmptyState'
import { Page } from '@/layout/Page'
import { AddPlayerDialog } from './AddPlayerDialog'
import { PlayerRow } from './PlayerRow'
import { squadQuery } from './squadQuery'

export function SquadPage() {
  const { data: user } = useQuery(currentUserQuery)
  const squad = useQuery(squadQuery)
  const isAdmin = user?.role === 'admin'

  return (
    <Page
      eyebrow="Atletico Hub"
      title="Rosa"
      description="I giocatori della rosa."
      actions={isAdmin ? <AddPlayerDialog /> : undefined}
    >
      {squad.isError && <p role="alert">Non riesco a caricare la rosa. Riprova tra poco.</p>}
      {squad.data?.items.length === 0 && <EmptyState icon={Users}>Nessun giocatore in rosa.</EmptyState>}
      {squad.data && squad.data.items.length > 0 && (
        <ul className="space-y-3">
          {squad.data.items.map((member) => (
            <PlayerRow key={member.id} member={member} isAdmin={isAdmin} />
          ))}
        </ul>
      )}
    </Page>
  )
}
