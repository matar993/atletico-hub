import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'

export const USERS_KEY = ['users'] as const

export const usersQuery = queryOptions({
  queryKey: USERS_KEY,
  queryFn: async () => {
    const { data } = await api.GET('/users')
    if (!data) throw new Error('Users: no data')
    return data
  },
})
