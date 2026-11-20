import { Bell, CalendarDays, CircleUser, ClipboardList, House, ShieldCheck, Users, type LucideIcon } from 'lucide-react'
import type { FileRoutesByTo } from '@/routeTree.gen'

export const TEAM_NAME = 'Atletico San Lorenzo'

export type NavEntry = {
  label: string
  to: keyof FileRoutesByTo
  icon: LucideIcon
  /** Shown to a user with the role `admin` only. The menu is the one place the web app reads the role. */
  adminOnly?: boolean
}

export const NAV_ENTRIES: readonly NavEntry[] = [
  { label: 'Home', to: '/', icon: House },
  { label: 'Eventi', to: '/events', icon: CalendarDays },
  { label: 'Convocazioni', to: '/call-ups', icon: ClipboardList },
  { label: 'Rosa', to: '/squad', icon: Users },
  { label: 'Notifiche', to: '/notifications', icon: Bell },
  { label: 'Profilo', to: '/profile', icon: CircleUser },
  { label: 'Utenti', to: '/users', icon: ShieldCheck, adminOnly: true },
]
