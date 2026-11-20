import createClient, { type Middleware } from 'openapi-fetch'
import type { paths } from './schema'

export const CSRF_HEADER = 'X-Requested-With'
export const CSRF_VALUE = 'atletico-hub'

const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

// A 401 from these routes is an answer for the page that asked, not an ended session: a wrong password on login, and
// the current-user check that the route guard of the sections handles itself. The invite routes are open.
function isOpenRoute(schemaPath: string) {
  return schemaPath === '/auth/login' || schemaPath === '/auth/me' || schemaPath.startsWith('/auth/invites/')
}

/**
 * Adds the CSRF header to every write, calls `onUnauthorized` on a 401 from any route that needs a session and
 * `onForbidden` on a 403 from any route.
 */
export function createAuthMiddleware(onUnauthorized: () => void, onForbidden: () => void = () => {}): Middleware {
  return {
    onRequest({ request }) {
      if (WRITE_METHODS.has(request.method)) {
        request.headers.set(CSRF_HEADER, CSRF_VALUE)
      }
      return request
    },
    onResponse({ response, schemaPath }) {
      if (response.status === 401 && !isOpenRoute(schemaPath)) {
        onUnauthorized()
      }
      if (response.status === 403) {
        onForbidden()
      }
      return response
    },
  }
}

// The API is reached on the web app's own origin, under /api.
export const api = createClient<paths>({ baseUrl: '/api' })
