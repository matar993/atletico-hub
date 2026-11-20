import { describe, expect, it } from 'vitest'
import { safeRedirect } from './safeRedirect'

describe('safeRedirect', () => {
  it.each(['/squad', '/events?x=1', '/'])('keeps the internal path %s', (path) => {
    expect(safeRedirect(path)).toBe(path)
  })

  it.each([undefined, '', 'https://evil.example', '//evil.example', '/\\evil.example', 'squad'])(
    'opens Home for %j',
    (value) => {
      expect(safeRedirect(value)).toBe('/')
    },
  )
})
