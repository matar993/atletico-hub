import { describe, expect, it } from 'vitest'
import { cn } from './cn'

describe('cn', () => {
  it('keeps the last of two conflicting Tailwind classes', () => {
    expect(cn('px-2 text-sm', 'px-4')).toBe('text-sm px-4')
  })

  it('drops falsy values', () => {
    expect(cn('a', false, null, undefined, 'c')).toBe('a c')
  })
})
