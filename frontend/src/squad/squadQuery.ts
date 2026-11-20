import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'

export const SQUAD_KEY = ['players'] as const

export const squadQuery = queryOptions({
  queryKey: SQUAD_KEY,
  queryFn: async () => {
    const { data } = await api.GET('/players')
    if (!data) throw new Error('Squad: no data')
    return data
  },
})
