import { expect, test, type Page } from '@playwright/test'
import { signIn } from './support/session'

test.beforeEach(({ page }) => signIn(page))

const isDark = (page: Page) => page.evaluate(() => document.documentElement.classList.contains('dark'))

async function chooseTheme(page: Page, label: 'Chiaro' | 'Scuro' | 'Sistema') {
  await page.getByRole('button', { name: 'Tema' }).click()
  await page.getByRole('menuitemradio', { name: label }).click()
}

test.use({ viewport: { width: 1280, height: 800 }, colorScheme: 'light' })

test('keeps the dark theme after a reload, with no wrong theme before the app starts', async ({ page }) => {
  await page.goto('/')
  await chooseTheme(page, 'Scuro')
  expect(await isDark(page)).toBe(true)

  // Stop the app bundle: only theme-init.js can set the class, so it is set before the first paint.
  await page.route('**/assets/*.js', (route) => route.abort())
  await page.reload()

  await expect(page.locator('#root')).toBeEmpty()
  expect(await isDark(page)).toBe(true)
})

test('"Sistema" follows the operating system theme', async ({ page }) => {
  await page.goto('/')
  await chooseTheme(page, 'Sistema')
  expect(await isDark(page)).toBe(false)

  await page.emulateMedia({ colorScheme: 'dark' })
  await expect.poll(() => isDark(page)).toBe(true)

  await page.emulateMedia({ colorScheme: 'light' })
  await expect.poll(() => isDark(page)).toBe(false)
})

test.describe('first visit on a dark system', () => {
  test.use({ colorScheme: 'dark' })

  test('shows the dark theme without any choice', async ({ page }) => {
    await page.goto('/')

    expect(await isDark(page)).toBe(true)
  })
})

test('chooses a theme with the keyboard only', async ({ page }) => {
  await page.goto('/')
  const trigger = page.getByRole('button', { name: 'Tema' })

  await trigger.focus()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('menu')).toBeVisible()
  await page.keyboard.press('ArrowDown')
  await expect(page.getByRole('menuitemradio', { name: 'Scuro' })).toBeFocused()
  await page.keyboard.press('Enter')

  await expect(page.getByRole('menu')).toBeHidden()
  await expect(trigger).toBeFocused()
  expect(await isDark(page)).toBe(true)
})

test('loads fonts, theme script and styles without a Content-Security-Policy violation', async ({ page }) => {
  const problems: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') problems.push(message.text())
  })
  page.on('pageerror', (error) => problems.push(error.message))

  await page.goto('/')
  await chooseTheme(page, 'Scuro')
  await page.getByRole('link', { name: 'Rosa' }).click()
  await page.evaluate(() => document.fonts.ready)

  expect(problems).toEqual([])
})
