import { createFileRoute } from '@tanstack/react-router'
import { PlaceholderPage } from '@/layout/PlaceholderPage'

export const Route = createFileRoute('/_authenticated/users')({
  component: () => (
    <PlaceholderPage title="Utenti" description="Gli account dell'app e i loro ruoli." emptyState="Nessun utente." />
  ),
})
