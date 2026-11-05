import { expect, test } from '@playwright/test'

test('home page shows the team name', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Atletico San Lorenzo' })).toBeVisible()
})
