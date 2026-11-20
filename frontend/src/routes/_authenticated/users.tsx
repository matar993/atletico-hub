import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { currentUserQuery } from '@/auth/currentUser'
import { NotAuthorizedPage } from '@/layout/NotAuthorizedPage'
import { UsersPage } from '@/users/UsersPage'

// The page is not rendered for a non-admin, so it makes no call to /users: the API would answer 403 anyway.
function UsersRoute() {
  const { data: user } = useQuery(currentUserQuery)
  return user?.role === 'admin' ? <UsersPage /> : <NotAuthorizedPage />
}

export const Route = createFileRoute('/_authenticated/users')({ component: UsersRoute })
