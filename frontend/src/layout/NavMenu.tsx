import { Link } from '@tanstack/react-router'
import { NAV_ENTRIES } from './navigation'

type NavMenuProps = {
  onNavigate?: () => void
}

export function NavMenu({ onNavigate }: NavMenuProps) {
  return (
    <nav aria-label="Menu principale">
      <ul className="space-y-1">
        {NAV_ENTRIES.map(({ label, to, icon: Icon }) => (
          <li key={to}>
            <Link
              to={to}
              activeOptions={{ exact: to === '/' }}
              onClick={onNavigate}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-700 hover:bg-slate-100"
              activeProps={{ className: 'bg-slate-200 font-semibold text-slate-900' }}
            >
              <Icon aria-hidden="true" className="size-5" />
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}
