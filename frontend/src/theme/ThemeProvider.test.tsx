import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ThemeProvider } from './ThemeProvider'
import { useTheme } from './useTheme'

type Listener = () => void

function stubSystemTheme(dark: boolean) {
  const listeners = new Set<Listener>()
  const media = {
    matches: dark,
    addEventListener: (_type: string, listener: Listener) => listeners.add(listener),
    removeEventListener: (_type: string, listener: Listener) => listeners.delete(listener),
  }
  vi.stubGlobal('matchMedia', () => media)
  return {
    set(next: boolean) {
      media.matches = next
      listeners.forEach((listener) => listener())
    },
  }
}

function Probe() {
  const { choice, setChoice } = useTheme()
  return (
    <>
      <p>choice: {choice}</p>
      <button onClick={() => setChoice('dark')}>dark</button>
    </>
  )
}

const isDark = () => document.documentElement.classList.contains('dark')

describe('ThemeProvider', () => {
  beforeEach(() => localStorage.clear())
  afterEach(() => {
    vi.unstubAllGlobals()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to the system theme', () => {
    stubSystemTheme(true)
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )

    expect(screen.getByText('choice: system')).toBeInTheDocument()
    expect(isDark()).toBe(true)
  })

  it('uses the saved choice over the system theme', () => {
    stubSystemTheme(false)
    localStorage.setItem('theme', 'dark')
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )

    expect(screen.getByText('choice: dark')).toBeInTheDocument()
    expect(isDark()).toBe(true)
  })

  it('saves a new choice and applies it at once', () => {
    stubSystemTheme(false)
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'dark' }))

    expect(localStorage.getItem('theme')).toBe('dark')
    expect(isDark()).toBe(true)
  })

  it('follows a system change while the choice is system', () => {
    const system = stubSystemTheme(false)
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )
    expect(isDark()).toBe(false)

    act(() => system.set(true))

    expect(isDark()).toBe(true)
  })

  it('ignores a system change once a theme is chosen', () => {
    const system = stubSystemTheme(false)
    localStorage.setItem('theme', 'light')
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )

    act(() => system.set(true))

    expect(isDark()).toBe(false)
  })

  it('works when storage throws', () => {
    stubSystemTheme(true)
    const blocked = () => {
      throw new Error('blocked')
    }
    vi.stubGlobal('localStorage', { getItem: blocked, setItem: blocked })
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    )
    expect(screen.getByText('choice: system')).toBeInTheDocument()
    expect(isDark()).toBe(true)

    fireEvent.click(screen.getByRole('button', { name: 'dark' }))

    expect(screen.getByText('choice: dark')).toBeInTheDocument()
  })
})
