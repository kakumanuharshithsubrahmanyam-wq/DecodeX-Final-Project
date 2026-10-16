# RTGS Frontend

## Current status — blocked on archive

**`rtgs-frontend.zip` is not in the workspace.** Searches of the repo root, Downloads, and Spotlight found no copy of the supplied frontend archive.

Per project rules, the Claude/Vite prototype cannot be recreated or faked. Integration, localization, auth wiring, and accessibility work **start only after** the zip is added.

### What to do

1. Copy `rtgs-frontend.zip` into the repository root:
   - `DecodeX Final Project/rtgs-frontend.zip`
2. Follow [docs/FRONTEND_IMPORT.md](../docs/FRONTEND_IMPORT.md).
3. Re-run the frontend integration task (Phases 1–9).

### Already in this folder (keep when merging)

| Path | Purpose |
|------|---------|
| `src/lib/api-client.ts` | FastAPI client, Bearer token, attachments |
| `src/lib/auth.ts` | Supabase browser client (anon key only) |
| `src/lib/types.ts` | Shared API types |
| `.env.example` | `VITE_API_BASE_URL`, `VITE_SUPABASE_*` |
| `src/vite-env.d.ts` | Vite env typing |

### Environment (browser-safe only)

```bash
cp .env.example .env.local
# VITE_API_BASE_URL=http://127.0.0.1:8000
# VITE_SUPABASE_URL=
# VITE_SUPABASE_ANON_KEY=
```

Never set `SUPABASE_SERVICE_ROLE_KEY` or backend secrets in `VITE_*` variables.

See [docs/FRONTEND_INTEGRATION.md](../docs/FRONTEND_INTEGRATION.md), [docs/API_CONTRACT.md](../docs/API_CONTRACT.md), [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md).
