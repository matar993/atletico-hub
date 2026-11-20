import { expect, test, type Page } from '@playwright/test'
import { signIn } from './support/session'

test.beforeEach(({ page }) => signIn(page))

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

// Records the left edge of the drawer on every frame while it opens: a slide shows up as negative values.
async function sampleDrawerLeft(page: Page) {
  await page.evaluate(() => {
    const samples: number[] = []
    ;(window as unknown as { drawerLeft: number[] }).drawerLeft = samples
    const start = performance.now()
    const tick = () => {
      const drawer = document.querySelector('[role="dialog"]')
      if (drawer) samples.push(Math.round(drawer.getBoundingClientRect().left))
      if (performance.now() - start < 1500) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  })
  await page.getByRole('button', { name: 'Apri il menu' }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.waitForTimeout(1500)
  return page.evaluate(() => (window as unknown as { drawerLeft: number[] }).drawerLeft)
}

test.describe('phone with motion', () => {
  test.use({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' })

  test('slides the drawer in', async ({ page }) => {
    await page.goto('/')

    const lefts = await sampleDrawerLeft(page)

    expect(Math.min(...lefts)).toBeLessThan(0)
    expect(lefts.at(-1)).toBe(0)
  })
})

test.describe('phone with reduced motion', () => {
  test.use({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' })

  test('shows the drawer without sliding', async ({ page }) => {
    await page.goto('/')

    const lefts = await sampleDrawerLeft(page)

    expect(lefts.length).toBeGreaterThan(0)
    expect(lefts.every((left) => left === 0)).toBe(true)
  })

  test('still opens and closes the drawer', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'Apri il menu' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await page.getByRole('button', { name: 'Chiudi il menu' }).click()

    await expect(page.getByRole('dialog')).toBeHidden()
  })
})
