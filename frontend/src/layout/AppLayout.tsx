import * as Dialog from '@radix-ui/react-dialog'
import { Outlet } from '@tanstack/react-router'
import { AnimatePresence, MotionConfig, motion } from 'framer-motion'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'
import { ThemeMenu } from '@/theme/ThemeMenu'
import { NavMenu } from './NavMenu'
import { TEAM_NAME } from './navigation'

const BRAND_MARK = TEAM_NAME.split(' ')
  .slice(0, 2)
  .map((word) => word[0])
  .join('')

const ICON_BUTTON =
  'inline-flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-raised hover:text-foreground'

export function AppLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  // reducedMotion="user": with prefers-reduced-motion the slide (a transform) is off and only the fade stays.
  return (
    <MotionConfig reducedMotion="user">
      <div className="min-h-screen bg-background text-foreground">
        <Dialog.Root open={drawerOpen} onOpenChange={setDrawerOpen}>
          <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur">
            <Dialog.Trigger aria-label="Apri il menu" className={`${ICON_BUTTON} md:hidden`}>
              <Menu aria-hidden="true" className="size-6" />
            </Dialog.Trigger>
            <span
              aria-hidden="true"
              className="flex size-9 items-center justify-center rounded-md bg-primary text-sm font-bold text-primary-foreground"
            >
              {BRAND_MARK}
            </span>
            <span className="text-lg font-semibold tracking-tight">{TEAM_NAME}</span>
            <div className="ml-auto">
              <ThemeMenu />
            </div>
          </header>

          <AnimatePresence>
            {drawerOpen && (
              <Dialog.Portal forceMount>
                <Dialog.Overlay asChild>
                  <motion.div
                    className="fixed inset-0 z-40 bg-black/50 md:hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  />
                </Dialog.Overlay>
                <Dialog.Content asChild aria-describedby={undefined}>
                  <motion.div
                    className="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col gap-4 border-r border-border bg-surface p-4 shadow-soft md:hidden"
                    initial={{ x: '-100%' }}
                    animate={{ x: 0 }}
                    exit={{ x: '-100%' }}
                    transition={{ duration: 0.25, ease: 'easeOut' }}
                  >
                    <div className="flex items-center justify-between">
                      <Dialog.Title className="px-3 text-sm font-semibold text-muted-foreground">Menu</Dialog.Title>
                      <Dialog.Close aria-label="Chiudi il menu" className={ICON_BUTTON}>
                        <X aria-hidden="true" className="size-6" />
                      </Dialog.Close>
                    </div>
                    <NavMenu onNavigate={() => setDrawerOpen(false)} />
                  </motion.div>
                </Dialog.Content>
              </Dialog.Portal>
            )}
          </AnimatePresence>
        </Dialog.Root>

        <div className="md:flex">
          <aside className="sticky top-16 hidden h-[calc(100vh-4rem)] w-64 shrink-0 flex-col justify-between border-r border-border bg-surface p-4 md:flex">
            <NavMenu />
            <p className="px-3 text-xs text-muted-foreground">Atletico Hub</p>
          </aside>

          <main className="min-w-0 flex-1 p-4 md:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </MotionConfig>
  )
}
