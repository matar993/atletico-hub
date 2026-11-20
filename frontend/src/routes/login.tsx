import { createFileRoute } from '@tanstack/react-router'
import { LoginPage } from '@/auth/LoginPage'

export const Route = createFileRoute('/login')({
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: typeof search.redirect === 'string' ? search.redirect : undefined,
  }),
  component: function Login() {
    return <LoginPage redirect={Route.useSearch().redirect} />
  },
})
