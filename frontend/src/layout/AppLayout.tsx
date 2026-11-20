import { Outlet } from '@tanstack/react-router'
import { Menu, X } from 'lucide-react'
import { useRef, useState } from 'react'
import { NavMenu } from './NavMenu'
import { TEAM_NAME } from './navigation'

const DRAWER_ID = 'nav-drawer'

export function AppLayout() {
  const drawerRef = useRef<HTMLDialogElement>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const openDrawer = () => {
    drawerRef.current?.showModal()
    setDrawerOpen(true)
  }
  const closeDrawer = () => drawerRef.current?.close()

  return (
    <div className="min-h-screen bg-white text-slate-900">
      <header className="flex items-center gap-3 border-b border-slate-200 px-4 py-3">
        <button
          type="button"
          onClick={openDrawer}
          aria-label="Apri il menu"
          aria-expanded={drawerOpen}
          aria-controls={DRAWER_ID}
          className="rounded-lg p-2 hover:bg-slate-100 md:hidden"
        >
          <Menu aria-hidden="true" className="size-6" />
        </button>
        <span className="text-lg font-semibold">{TEAM_NAME}</span>
      </header>

      <div className="md:flex">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 p-4 md:block">
          <NavMenu />
        </aside>

        {/* Backdrop click is a mouse shortcut; keyboard users close with Escape or the close button. */}
        {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-noninteractive-element-interactions */}
        <dialog
          ref={drawerRef}
          id={DRAWER_ID}
          aria-label="Menu"
          onClose={() => setDrawerOpen(false)}
          onClick={(event) => {
            if (event.target === event.currentTarget) closeDrawer()
          }}
          className="m-0 h-full max-h-none w-72 max-w-[85vw] bg-white p-4 backdrop:bg-black/40 md:hidden"
        >
          <button
            type="button"
            onClick={closeDrawer}
            aria-label="Chiudi il menu"
            className="mb-4 rounded-lg p-2 hover:bg-slate-100"
          >
            <X aria-hidden="true" className="size-6" />
          </button>
          <NavMenu onNavigate={closeDrawer} />
        </dialog>

        <main className="min-w-0 flex-1 p-4">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
