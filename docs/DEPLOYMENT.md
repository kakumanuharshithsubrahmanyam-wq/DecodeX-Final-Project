# RTGS Deployment Readiness (Phase 4)

**Not production-deployed in Phase 4.** This document describes how to deploy when ready.

## Prerequisites

- Dedicated **development** Supabase project for RTGS (do not reuse unrelated projects without review).
- Migrations applied in order (see README).
- Private Storage bucket `complaint-attachments` ([supabase/storage/complaint-attachments-policy.md](../supabase/storage/complaint-attachments-policy.md)).
- Claude frontend imported under `frontend/` with `npm run build` working.

## Backend — Render

1. Connect this repository to Render.
2. Use [render.yaml](../render.yaml) or create a Web Service:
   - Root directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check: `/api/v1/health`
3. Set environment variables (dashboard only — never commit):
   - `APP_ENV=production`
   - `AUTH_DEV_BYPASS=false` (required; app refuses startup if bypass is on in production)
   - `DATABASE_URL` (Supabase pooler, async: `postgresql+asyncpg://...`)
   - `SUPABASE_URL`, `SUPABASE_JWT_SECRET` and/or JWKS via default URL
   - `SUPABASE_SERVICE_ROLE_KEY` (server only)
   - `JWT_ISSUER`, `JWT_AUDIENCE`
   - `CORS_ORIGINS` = your Vercel URL(s), comma-separated
4. Verify `GET /api/v1/health` returns `"database": "ok"`.

## Frontend — Vercel

**Blocked until Claude UI exists** (see [frontend/README.md](../frontend/README.md)).

When ready:

1. Import repo; set root directory to `frontend`.
2. Framework preset: Vite.
3. Environment (public only):
   - `VITE_API_BASE_URL` → Render API URL
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
4. Do **not** set service role or JWT secret on Vercel.

## Supabase dev setup (manual)

```bash
# Link your RTGS dev project only
supabase link --project-ref YOUR_RTGS_DEV_REF

# Inspect remote migration state before push
supabase migration list

# Apply pending migrations (non-destructive forward-only)
supabase db push

# Seed only on empty/dev DB
psql "$DATABASE_URL" -f supabase/seed.sql
```

Provision roles: [backend/docs/ACCOUNT_PROVISIONING.md](../backend/docs/ACCOUNT_PROVISIONING.md).

## Smoke test

Follow [docs/SMOKE_TEST.md](./SMOKE_TEST.md) after dev env is configured.

## CI

GitHub Actions runs backend pytest on push/PR (SQLite mocks). Live Supabase tests are manual (`pytest -m live` when configured).
