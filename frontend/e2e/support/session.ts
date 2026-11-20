import type { Page } from '@playwright/test'

export const USER = { first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'player' }

/** Stubs the API calls of a signed-in user: the browser tests run on the production build with no API behind them. */
export async function signIn(page: Page, user: typeof USER = USER) {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: user }))
  await page.route('**/api/players', (route) => route.fulfill({ json: { permissions: { create: false }, items: [] } }))
}

/** Stubs the current-user check as a user without a session. */
export async function signedOut(page: Page) {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: { detail: 'Not signed in' } }))
}
