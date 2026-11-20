import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createRouter, RouterProvider } from '@tanstack/react-router'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CURRENT_USER_KEY } from './auth/currentUser'
import { api, createAuthMiddleware } from './lib/api/client'
import { routeTree } from './routeTree.gen'
import '@fontsource/inter/latin-400.css'
import '@fontsource/inter/latin-500.css'
import '@fontsource/inter/latin-600.css'
import '@fontsource/inter/latin-700.css'
import '@fontsource/jetbrains-mono/latin-400.css'
import '@fontsource/jetbrains-mono/latin-500.css'
import './styles/globals.css'

const queryClient = new QueryClient()
const router = createRouter({ routeTree, context: { queryClient } })

// A 401 from any route that needs a session: forget the user and go to login, then back to this page.
// A 403 from any route: the user may have lost a permission during the session, so show the not authorized page.
api.use(
  createAuthMiddleware(
    () => {
      queryClient.removeQueries({ queryKey: CURRENT_USER_KEY })
      void router.navigate({ to: '/login', search: { redirect: router.state.location.href } })
    },
    () => {
      // The role may have changed: reload it, so the menu and /users stop offering what the user lost.
      void queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY })
      void router.navigate({ to: '/forbidden' })
    },
  ),
)

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
