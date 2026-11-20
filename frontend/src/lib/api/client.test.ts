import createClient from 'openapi-fetch'
import { describe, expect, it, vi } from 'vitest'
import { CSRF_HEADER, CSRF_VALUE, createAuthMiddleware } from './client'
import type { paths } from './schema'

function setup(status = 200) {
  const onUnauthorized = vi.fn()
  const onForbidden = vi.fn()
  const fetchMock = vi.fn(async () => new Response(status === 204 ? null : '{}', { status }))
  const client = createClient<paths>({ baseUrl: 'http://localhost/api', fetch: fetchMock })
  client.use(createAuthMiddleware(onUnauthorized, onForbidden))
  const sentRequest = () => (fetchMock.mock.calls[0] as unknown as [Request])[0]
  return { client, onUnauthorized, onForbidden, sentRequest }
}

describe('auth middleware', () => {
  it('adds the CSRF header to a write', async () => {
    const { client, sentRequest } = setup()

    await client.POST('/auth/logout')

    expect(sentRequest().headers.get(CSRF_HEADER)).toBe(CSRF_VALUE)
  })

  it('does not add the CSRF header to a read', async () => {
    const { client, sentRequest } = setup()

    await client.GET('/players')

    expect(sentRequest().headers.get(CSRF_HEADER)).toBeNull()
  })

  it('calls onUnauthorized on a 401 from a route that needs a session', async () => {
    const { client, onUnauthorized } = setup(401)

    await client.GET('/players')

    expect(onUnauthorized).toHaveBeenCalledOnce()
  })

  it('calls onForbidden on a 403 and not onUnauthorized', async () => {
    const { client, onUnauthorized, onForbidden } = setup(403)

    await client.GET('/players')

    expect(onForbidden).toHaveBeenCalledOnce()
    expect(onUnauthorized).not.toHaveBeenCalled()
  })

  it('does not call onForbidden on a 401 or a success', async () => {
    const unauthorized = setup(401)
    const ok = setup(200)

    await unauthorized.client.GET('/players')
    await ok.client.GET('/players')

    expect(unauthorized.onForbidden).not.toHaveBeenCalled()
    expect(ok.onForbidden).not.toHaveBeenCalled()
  })

  // A rule that refuses an action answers 409: the page shows its message, the user stays on it.
  it('does not call onForbidden on a 409', async () => {
    const { client, onForbidden } = setup(409)

    await client.POST('/auth/invites', { body: { player_id: 1 } })

    expect(onForbidden).not.toHaveBeenCalled()
  })

  it.each([
    [
      'login',
      () => (c: ReturnType<typeof setup>['client']) =>
        c.POST('/auth/login', { body: { email: 'a@b.it', password: 'x' } }),
    ],
    ['the current-user check', () => (c: ReturnType<typeof setup>['client']) => c.GET('/auth/me')],
    [
      'an invite route',
      () => (c: ReturnType<typeof setup>['client']) =>
        c.GET('/auth/invites/{token}', { params: { path: { token: 't' } } }),
    ],
  ])('does not call onUnauthorized on a 401 from %s', async (_name, call) => {
    const { client, onUnauthorized } = setup(401)

    await call()(client)

    expect(onUnauthorized).not.toHaveBeenCalled()
  })

  it('does not call onUnauthorized on a success', async () => {
    const { client, onUnauthorized } = setup(200)

    await client.GET('/players')

    expect(onUnauthorized).not.toHaveBeenCalled()
  })
})
