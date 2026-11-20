import { describe, expect, it } from 'vitest'
import { apiErrorMessage } from './errors'

describe('apiErrorMessage', () => {
  it('returns the detail of the API', () => {
    expect(apiErrorMessage({ detail: 'Email o password non corretti' })).toBe('Email o password non corretti')
  })

  it.each([[undefined], [{}], [{ detail: [{ msg: 'x' }] }], ['text']])('returns a generic message for %j', (error) => {
    expect(apiErrorMessage(error)).toBe('Errore imprevisto, riprova.')
  })
})
