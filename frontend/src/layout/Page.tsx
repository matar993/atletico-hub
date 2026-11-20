import type { ReactNode } from 'react'

type PageProps = {
  title: string
  description: string
  eyebrow?: string
  actions?: ReactNode
  children?: ReactNode
}

export function Page({ title, description, eyebrow, actions, children }: PageProps) {
  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-1">
          {eyebrow && <p className="text-xs font-semibold tracking-wider text-primary uppercase">{eyebrow}</p>}
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </header>
      {children}
    </section>
  )
}
