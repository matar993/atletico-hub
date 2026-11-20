import { Page } from '@/layout/Page'
import { Panel } from './Panel'
import { SAMPLE_PANELS } from './sampleContent'

export function HomePage() {
  return (
    <Page eyebrow="Atletico Hub" title="Home" description="Il riepilogo della squadra: prossimi eventi e novità.">
      <div className="grid gap-4 lg:grid-cols-3">
        {SAMPLE_PANELS.map(({ title, to, icon, rows }) => (
          <Panel key={to} title={title} to={to} icon={icon}>
            <ul className="divide-y divide-border">
              {rows.map(({ title: rowTitle, detail }) => (
                <li key={rowTitle} className="py-2 first:pt-0 last:pb-0">
                  <p className="text-sm font-medium">{rowTitle}</p>
                  <p className="text-sm text-muted-foreground">{detail}</p>
                </li>
              ))}
            </ul>
          </Panel>
        ))}
      </div>
    </Page>
  )
}
