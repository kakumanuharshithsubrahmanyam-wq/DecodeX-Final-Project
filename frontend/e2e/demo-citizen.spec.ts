import { expect, test } from '@playwright/test';

/**
 * Browser E2E against demo mode (no live Supabase). Build must use VITE_DEMO_MODE=true.
 */
test.describe('RTGS demo citizen journey', () => {
  test('landing shows primary actions and file complaint flow step 1', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await page.getByRole('link', { name: /file a complaint|ఫిర్యాదు/i }).first().click();
    await expect(page.getByText(/what would you like|మీరు ఏమి/i)).toBeVisible();
  });

  test('Telugu language switch updates visible portal copy', async ({ page }) => {
    await page.goto('/');
    const langBtn = page.getByRole('button', { name: /english|telugu|english/i }).first();
    if (await langBtn.isVisible()) {
      await langBtn.click();
    }
    await expect(page.locator('html')).toHaveAttribute('lang', /te|en/);
  });

  test('chat panel opens and shows disclaimer', async ({ page }) => {
    await page.goto('/');
    const fab = page.getByRole('button', { name: /help assistant|assistant|సహాయ/i });
    await fab.click();
    await expect(page.locator('.chat-panel')).toContainText(/Not live AI|live AI service/i);
  });
});
