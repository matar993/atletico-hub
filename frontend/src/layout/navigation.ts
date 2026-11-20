import { Bell, CalendarDays, CircleUser, ClipboardList, House, Users, type LucideIcon } from 'lucide-react'
import type { FileRoutesByTo } from '@/routeTree.gen'

export const TEAM_NAME = 'Atletico San Lorenzo'

export type NavEntry = {
  label: string
  to: keyof FileRoutesByTo
  icon: LucideIcon
}

export const NAV_ENTRIES: readonly NavEntry[] = [
  { label: 'Home', to: '/', icon: House },
  { label: 'Eventi', to: '/events', icon: CalendarDays },
  { label: 'Convocazioni', to: '/call-ups', icon: ClipboardList },
  { label: 'Rosa', to: '/squad', icon: Users },
  { label: 'Notifiche', to: '/notifications', icon: Bell },
  { label: 'Profilo', to: '/profile', icon: CircleUser },
]
