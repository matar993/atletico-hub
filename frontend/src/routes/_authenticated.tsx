import { createFileRoute, redirect } from '@tanstack/react-router'
import { currentUserQuery, UnauthorizedError } from '@/auth/currentUser'
import { AppLayout } from '@/layout/AppLayout'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ context, location }) => {
    try {
      await context.queryClient.ensureQueryData(currentUserQuery)
    } catch (error) {
      if (error instanceof UnauthorizedError) {
        throw redirect({ to: '/login', search: { redirect: location.href } })
      }
      throw error
    }
  },
  component: AppLayout,
})
