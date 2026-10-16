import { test } from '@playwright/test';

/**
 * Live Supabase + API E2E — skipped unless E2E_LIVE=1 and credentials in env (never committed).
 * Set PLAYWRIGHT_BASE_URL to deployed Vercel URL when testing production-like staging.
 */
test.describe('RTGS live integration', () => {
  test.skip(process.env.E2E_LIVE !== '1', 'Set E2E_LIVE=1 with Supabase and API env to run live browser tests');

  test('placeholder live login', async () => {
    // Implemented when rtgs-dev Supabase project and test accounts exist.
  });
});
