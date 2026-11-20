type PlaceholderPageProps = {
  title: string
  description: string
  emptyState: string
}

export function PlaceholderPage({ title, description, emptyState }: PlaceholderPageProps) {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="text-slate-600">{description}</p>
      <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-slate-500">{emptyState}</p>
    </section>
  )
}
