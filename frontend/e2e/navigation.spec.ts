import { expect, test } from '@playwright/test'

const SECTIONS = [
  { label: 'Home', path: '/' },
  { label: 'Eventi', path: '/events' },
  { label: 'Convocazioni', path: '/call-ups' },
  { label: 'Rosa', path: '/squad' },
  { label: 'Notifiche', path: '/notifications' },
  { label: 'Profilo', path: '/profile' },
]

test.describe('desktop', () => {
  test.use({ viewport: { width: 1280, height: 800 } })

  test('shows the sidebar and no hamburger button', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByText('Atletico San Lorenzo')).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Menu principale' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Apri il menu' })).toBeHidden()
  })

  test('reaches every section from the menu', async ({ page }) => {
    await page.goto('/')
    const menu = page.getByRole('navigation', { name: 'Menu principale' })

    for (const { label, path } of SECTIONS) {
      await menu.getByRole('link', { name: label }).click()

      await expect(page).toHaveURL(path)
      await expect(page.getByRole('heading', { name: label })).toBeVisible()
      await expect(menu.getByRole('link', { name: label })).toHaveAttribute('aria-current', 'page')
      await expect(menu.locator('[aria-current="page"]')).toHaveCount(1)
    }
  })
})

test.describe('phone', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('hides the menu until the hamburger button is used', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('navigation', { name: 'Menu principale' })).toBeHidden()
    await expect(page.getByRole('button', { name: 'Apri il menu' })).toBeVisible()
  })

  test('opens the drawer, navigates and closes it', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'Apri il menu' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await page.getByRole('link', { name: 'Rosa' }).click()

    await expect(page).toHaveURL('/squad')
    await expect(page.getByRole('heading', { name: 'Rosa' })).toBeVisible()
    await expect(page.getByRole('dialog')).toBeHidden()
  })

  test('closes the drawer with Escape without navigating', async ({ page }) => {
    await page.goto('/events')

    await page.getByRole('button', { name: 'Apri il menu' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await page.keyboard.press('Escape')

    await expect(page.getByRole('dialog')).toBeHidden()
    await expect(page).toHaveURL('/events')
  })
})
