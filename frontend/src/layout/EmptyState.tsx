import type { LucideIcon } from 'lucide-react'

type EmptyStateProps = {
  icon: LucideIcon
  children: string
}

export function EmptyState({ icon: Icon, children }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-border bg-surface p-10 text-center">
      <span className="flex size-12 items-center justify-center rounded-full bg-accent text-accent-foreground">
        <Icon aria-hidden="true" className="size-6" />
      </span>
      <p className="text-muted-foreground">{children}</p>
    </div>
  )
}
