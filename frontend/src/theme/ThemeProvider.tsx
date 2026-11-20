import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { THEME_STORAGE_KEY, ThemeContext, type ThemeChoice } from './useTheme'

const DARK_QUERY = '(prefers-color-scheme: dark)'

function readChoice(): ThemeChoice {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    // Storage blocked: fall back to the system theme.
  }
  return 'system'
}

function saveChoice(choice: ThemeChoice) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, choice)
  } catch {
    // Storage blocked: the choice lasts until the page closes.
  }
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>(readChoice)

  useEffect(() => {
    const media = window.matchMedia(DARK_QUERY)
    const apply = () => {
      document.documentElement.classList.toggle('dark', choice === 'dark' || (choice === 'system' && media.matches))
    }
    apply()
    if (choice !== 'system') return
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [choice])

  const value = useMemo(
    () => ({
      choice,
      setChoice: (next: ThemeChoice) => {
        saveChoice(next)
        setChoiceState(next)
      },
    }),
    [choice],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
