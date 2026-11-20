import { Link } from '@tanstack/react-router'
import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import type { FileRoutesByTo } from '@/routeTree.gen'

type PanelProps = {
  title: string
  to: keyof FileRoutesByTo
  icon: LucideIcon
  children: ReactNode
}

export function Panel({ title, to, icon: Icon, children }: PanelProps) {
  return (
    <section className="space-y-4 rounded-lg border border-border bg-surface p-5 shadow-soft">
      <div className="flex items-center gap-3">
        <span className="flex size-9 items-center justify-center rounded-md bg-accent text-accent-foreground">
          <Icon aria-hidden="true" className="size-5" />
        </span>
        <h2 className="font-semibold">
          <Link to={to} className="hover:underline">
            {title}
          </Link>
        </h2>
        <span className="ml-auto rounded-full bg-surface-raised px-2 py-0.5 text-xs font-medium text-muted-foreground">
          Anteprima
        </span>
      </div>
      {children}
    </section>
  )
}
