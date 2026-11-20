import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { ThemeMenu } from './ThemeMenu'
import { ThemeProvider } from './ThemeProvider'

const isDark = () => document.documentElement.classList.contains('dark')

function openMenu() {
  fireEvent.keyDown(screen.getByRole('button', { name: 'Tema' }), { key: 'Enter' })
}

describe('ThemeMenu', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    render(
      <ThemeProvider>
        <ThemeMenu />
      </ThemeProvider>,
    )
  })

  it('offers the three choices, with Sistema selected by default', () => {
    openMenu()

    expect(screen.getAllByRole('menuitemradio').map((item) => item.textContent)).toEqual(['Chiaro', 'Scuro', 'Sistema'])
    expect(screen.getByRole('menuitemradio', { name: 'Sistema' })).toBeChecked()
  })

  it('sets the dark theme when Scuro is chosen', () => {
    openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: 'Scuro' }))

    expect(isDark()).toBe(true)
    openMenu()
    expect(screen.getByRole('menuitemradio', { name: 'Scuro' })).toBeChecked()
  })

  it('sets the light theme when Chiaro is chosen after Scuro', () => {
    openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: 'Scuro' }))
    openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: 'Chiaro' }))

    expect(isDark()).toBe(false)
  })

  it('goes back to the system theme when Sistema is chosen', () => {
    openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: 'Scuro' }))
    openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: 'Sistema' }))

    expect(isDark()).toBe(false)
    expect(localStorage.getItem('theme')).toBe('system')
  })
})
