# RTGS Frontend

React + TypeScript + Vite application integrated with the FastAPI backend and Supabase Auth.

## Run locally

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Environment (browser-safe only)

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | FastAPI base URL (e.g. `http://127.0.0.1:8000`) |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Publishable / anon key only |
| `VITE_DEMO_MODE` | `true` — UI preview with **labeled** Hyderabad sample data when Supabase is not configured (never use in production) |

Never set `SUPABASE_SERVICE_ROLE_KEY` or backend secrets in `VITE_*` variables.

## Scripts

- `npm run dev` — development server
- `npm run build` — production bundle
- `npm test` — Vitest (includes English/Telugu dictionary key parity)
- `npm run typecheck` — TypeScript

## Architecture

| Path | Role |
|------|------|
| `src/RtgsPortal.tsx` | Supplied UI (citizen/officer/admin workflows) |
| `src/App.tsx` | Auth routes and guards |
| `src/auth/` | Supabase session + `GET /api/v1/me` role |
| `src/data/GrievanceContext.tsx` | Live API vs isolated demo sample data |
| `src/lib/api-client.ts` | FastAPI client + attachment signed URLs |
| `src/i18n/` | English/Telugu dictionaries and `document.lang` |

## Roles

- **Citizens:** register via Supabase Auth; profile role `citizen` from DB trigger `handle_new_user`.
- **Staff:** provisioned server-side per [backend/docs/ACCOUNT_PROVISIONING.md](../backend/docs/ACCOUNT_PROVISIONING.md).

## Connected vs local-only

| Feature | Backend |
|---------|---------|
| Auth, `/me`, grievances, analyze, attachments, notifications, officer transitions (live mode) | FastAPI + Supabase |
| Community posts | Local demo only (no community API in MVP) |
| Sample Hyderabad records | `VITE_DEMO_MODE` or explicit demo data mode only |
| Admin chart history (partial months) | Illustrative where not from API analytics |

See [docs/FRONTEND_INTEGRATION.md](../docs/FRONTEND_INTEGRATION.md) and [docs/SMOKE_TEST.md](../docs/SMOKE_TEST.md).
