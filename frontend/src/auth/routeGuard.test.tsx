import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '@/lib/api/client'
import { renderApp } from '@/test/renderApp'

vi.mock('@/lib/api/client', () => ({ api: { GET: vi.fn(), POST: vi.fn() } }))

describe('authenticated routes', () => {
  beforeEach(() => {
    vi.mocked(api.GET).mockResolvedValue({
      error: { detail: 'Not signed in' },
      response: new Response(null, { status: 401 }),
    } as never)
  })

  it('redirects to login with the requested path when the current user answers 401', async () => {
    const { router } = await renderApp('/squad')

    expect(router.state.location.pathname).toBe('/login')
    expect(router.state.location.search).toEqual({ redirect: '/squad' })
  })

  it('rethrows an error of the current user check that is not a 401', async () => {
    vi.mocked(api.GET).mockResolvedValue({ response: new Response(null, { status: 500 }) } as never)

    const { router } = await renderApp('/squad')

    expect(router.state.location.pathname).not.toBe('/login')
  })
})
