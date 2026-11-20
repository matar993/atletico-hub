import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => cleanup())

// jsdom does not implement scrolling; the router calls it on navigation.
window.scrollTo = () => {}

// jsdom does not implement matchMedia; tests that need a dark system theme stub it themselves.
window.matchMedia = (query: string) =>
  ({
    matches: false,
    media: query,
    addEventListener: () => {},
    removeEventListener: () => {},
  }) as unknown as MediaQueryList

// Node 26 defines its own `localStorage` global that is unusable without --localstorage-file and hides the one of
// jsdom. Tests get a plain in-memory one.
const memory = new Map<string, string>()
Object.defineProperty(globalThis, 'localStorage', {
  configurable: true,
  value: {
    getItem: (key: string) => memory.get(key) ?? null,
    setItem: (key: string, value: string) => void memory.set(key, String(value)),
    removeItem: (key: string) => void memory.delete(key),
    clear: () => memory.clear(),
  },
})
