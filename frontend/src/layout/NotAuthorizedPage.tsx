import { Link } from '@tanstack/react-router'
import { ShieldAlert } from 'lucide-react'
import { BUTTON_SECONDARY } from '@/ui/classes'
import { EmptyState } from './EmptyState'
import { Page } from './Page'

export function NotAuthorizedPage() {
  return (
    <Page eyebrow="Atletico Hub" title="Accesso negato" description="Questa sezione non è per te.">
      <EmptyState icon={ShieldAlert}>Non hai i permessi per vedere questa pagina</EmptyState>
      <div className="flex justify-center">
        <Link to="/" className={BUTTON_SECONDARY}>
          Torna alla Home
        </Link>
      </div>
    </Page>
  )
}
