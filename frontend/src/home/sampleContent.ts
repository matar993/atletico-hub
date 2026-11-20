import { Bell, CalendarDays, ClipboardList, type LucideIcon } from 'lucide-react'
import type { FileRoutesByTo } from '@/routeTree.gen'

// Static sample content: not data of the team, not an API mock. Delete it when the real features land.
export type SamplePanel = {
  title: string
  to: keyof FileRoutesByTo
  icon: LucideIcon
  rows: readonly { title: string; detail: string }[]
}

export const SAMPLE_PANELS: readonly SamplePanel[] = [
  {
    title: 'Prossimi eventi',
    to: '/events',
    icon: CalendarDays,
    rows: [
      { title: 'Allenamento', detail: 'Martedì, 19:00' },
      { title: 'Partita di campionato', detail: 'Domenica, 15:30' },
    ],
  },
  {
    title: 'Convocazioni',
    to: '/call-ups',
    icon: ClipboardList,
    rows: [{ title: 'Partita di campionato', detail: 'Risposta da dare' }],
  },
  {
    title: 'Notifiche',
    to: '/notifications',
    icon: Bell,
    rows: [{ title: 'Allenamento spostato alle 20:00', detail: 'Ieri' }],
  },
]
