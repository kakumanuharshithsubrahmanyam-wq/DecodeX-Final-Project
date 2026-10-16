# RTGS Frontend — Integration status (Phase 4)

## Blocker

**Claude's UI is not present in this repository.** The `frontend/` directory currently contains:

- `.env.example`
- Shared integration helpers under `src/lib/` (API client, auth helper, types)
- This README

There is **no** Vite app, `package.json`, routes, or visual design to integrate yet.

## When Claude delivers the UI

1. Import Claude's React + Vite + Tailwind project **into this folder** without replacing its visual design.
2. Copy `.env.example` → `.env.local` and set:
   - `VITE_API_BASE_URL`
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
3. Wire screens to `@/lib/api-client` and `@/lib/auth` (adjust import paths to match Claude's alias config).
4. Follow [docs/FRONTEND_INTEGRATION.md](../docs/FRONTEND_INTEGRATION.md) and [docs/API_CONTRACT.md](../docs/API_CONTRACT.md).
5. Run `npm run dev` and verify against a local or dev backend.

## Do not

- Embed `SUPABASE_SERVICE_ROLE_KEY` or any backend secret in frontend env vars.
- Claim success for API calls without checking response status and error envelopes.

See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for Vercel deployment after the app exists.
