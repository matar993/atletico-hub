import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { motion } from 'framer-motion'
import { useId } from 'react'
import { currentUserQuery } from '@/auth/currentUser'
import { NAV_ENTRIES } from './navigation'

type NavMenuProps = {
  onNavigate?: () => void
}

export function NavMenu({ onNavigate }: NavMenuProps) {
  // The sidebar and the drawer both render this menu: each needs its own marker, or the two would animate as one.
  const markerId = useId()
  const { data: user } = useQuery(currentUserQuery)
  const entries = NAV_ENTRIES.filter((entry) => !entry.adminOnly || user?.role === 'admin')

  return (
    <nav aria-label="Menu principale">
      <ul className="space-y-1">
        {entries.map(({ label, to, icon: Icon }) => (
          <li key={to}>
            <Link
              to={to}
              activeOptions={{ exact: to === '/' }}
              onClick={onNavigate}
              className="relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              activeProps={{ className: 'text-accent-foreground hover:text-accent-foreground' }}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId={markerId}
                      aria-hidden="true"
                      className="absolute inset-0 rounded-md bg-accent"
                      transition={{ type: 'spring', stiffness: 500, damping: 40 }}
                    />
                  )}
                  <Icon aria-hidden="true" className="relative size-5" />
                  <span className="relative">{label}</span>
                </>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}
