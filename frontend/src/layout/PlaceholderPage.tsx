import { Inbox } from 'lucide-react'
import { EmptyState } from './EmptyState'
import { Page } from './Page'

type PlaceholderPageProps = {
  title: string
  description: string
  emptyState: string
}

export function PlaceholderPage({ title, description, emptyState }: PlaceholderPageProps) {
  return (
    <Page eyebrow="Atletico Hub" title={title} description={description}>
      <EmptyState icon={Inbox}>{emptyState}</EmptyState>
    </Page>
  )
}
