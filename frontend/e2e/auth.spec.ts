import { expect, test } from '@playwright/test'
import { signedOut, signIn, USER } from './support/session'

test.use({ viewport: { width: 1280, height: 800 } })

test('a section without a session opens login and returns to it after login', async ({ page }) => {
  await signedOut(page)
  await page.route('**/api/players', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/auth/login', (route) => route.fulfill({ json: USER }))

  await page.goto('/squad')

  await expect(page).toHaveURL(/\/login\?redirect=%2Fsquad$/)
  await page.getByLabel('Email').fill('anna@example.com')
  await page.getByLabel('Password').fill('secret-pass')
  await page.getByRole('button', { name: 'Accedi' }).click()

  await expect(page).toHaveURL('/squad')
  await expect(page.getByRole('heading', { name: 'Rosa' })).toBeVisible()
})

test('logout opens login, and a section then asks for login again', async ({ page }) => {
  await signIn(page)
  await page.route('**/api/auth/logout', (route) => route.fulfill({ status: 204 }))

  await page.goto('/')
  await expect(page.getByText('Anna Rossi')).toBeVisible()
  await page.getByRole('button', { name: 'Esci' }).click()

  await expect(page).toHaveURL('/login')
  await page.unroute('**/api/auth/me')
  await signedOut(page)
  await page.goto('/events')
  await expect(page).toHaveURL(/\/login\?redirect=%2Fevents$/)
})
