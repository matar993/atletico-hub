import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { currentUserQuery } from '@/auth/currentUser'
import { NotAuthorizedPage } from '@/layout/NotAuthorizedPage'
import { PlaceholderPage } from '@/layout/PlaceholderPage'

function UsersRoute() {
  const { data: user } = useQuery(currentUserQuery)
  if (user?.role !== 'admin') return <NotAuthorizedPage />
  return (
    <PlaceholderPage title="Utenti" description="Gli account dell'app e i loro ruoli." emptyState="Nessun utente." />
  )
}

export const Route = createFileRoute('/_authenticated/users')({ component: UsersRoute })
