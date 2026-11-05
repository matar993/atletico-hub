import createClient from 'openapi-fetch'
import type { paths } from './schema'

// The API is reached on the web app's own origin, under /api.
export const api = createClient<paths>({ baseUrl: '/api' })
