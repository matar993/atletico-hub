import { expect, test } from '@playwright/test'
import { signIn, USER } from './support/session'

test.use({ viewport: { width: 1280, height: 800 } })

const ADMIN = { ...USER, role: 'admin' }

test('an admin changes the role of a player in Utenti', async ({ page }) => {
  await signIn(page, ADMIN)
  const accounts = [
    { id: 1, first_name: 'Luca', last_name: 'Bianchi', email: 'luca@example.com', role: 'player' },
    { id: 2, first_name: 'Anna', last_name: 'Rossi', email: 'anna@example.com', role: 'admin' },
  ]
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: { items: accounts.map((a) => ({ ...a, permissions: { change_role: true } })) } }),
  )
  await page.route('**/api/users/1/role', (route) => {
    accounts[0].role = 'admin'
    return route.fulfill({ json: { id: 1, role: 'admin' } })
  })

  await page.goto('/users')
  await expect(page.getByRole('heading', { name: 'Utenti' })).toBeVisible()
  await page.getByLabel('Ruolo di Luca Bianchi').selectOption('admin')

  await expect(page.getByLabel('Ruolo di Luca Bianchi')).toHaveValue('admin')
})

test('an admin sees the message of the API when the last admin is refused', async ({ page }) => {
  await signIn(page, ADMIN)
  await page.route('**/api/users', (route) =>
    route.fulfill({
      json: {
        items: [
          {
            id: 2,
            first_name: 'Anna',
            last_name: 'Rossi',
            email: 'anna@example.com',
            role: 'admin',
            permissions: { change_role: true },
          },
        ],
      },
    }),
  )
  await page.route('**/api/users/2/role', (route) =>
    route.fulfill({ status: 409, json: { detail: 'Serve almeno un admin' } }),
  )

  await page.goto('/users')
  await page.getByLabel('Ruolo di Anna Rossi').selectOption('player')

  await expect(page.getByText('Serve almeno un admin')).toBeVisible()
  await expect(page.getByLabel('Ruolo di Anna Rossi')).toHaveValue('admin')
})

test('a player who opens /users sees the not authorized page and no Utenti entry', async ({ page }) => {
  await signIn(page)

  await page.goto('/users')

  await expect(page.getByText('Non hai i permessi per vedere questa pagina')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Torna alla Home' })).toBeVisible()
  await expect(
    page.getByRole('navigation', { name: 'Menu principale' }).getByRole('link', { name: 'Utenti' }),
  ).toHaveCount(0)
})
