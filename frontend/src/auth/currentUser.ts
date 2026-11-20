import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'

export class UnauthorizedError extends Error {
  constructor() {
    super('Not signed in')
  }
}

export const CURRENT_USER_KEY = ['auth', 'me'] as const

export const currentUserQuery = queryOptions({
  queryKey: CURRENT_USER_KEY,
  queryFn: async () => {
    const { data, response } = await api.GET('/auth/me')
    if (response.status === 401) throw new UnauthorizedError()
    if (!data) throw new Error(`Current user: unexpected status ${response.status}`)
    return data
  },
})
