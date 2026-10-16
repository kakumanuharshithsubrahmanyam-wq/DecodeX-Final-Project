# RTGS Deployment Readiness

**Phase 7.5:** Integrated deploy not completed — Supabase `rtgs-dev` blocked by org free-project limit; Render CLI not logged in. See [PHASE7_5_VERIFICATION.md](./PHASE7_5_VERIFICATION.md).

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

# Private storage bucket
psql "$DATABASE_URL" -f supabase/scripts/create_storage_bucket.sql
```

Full runbook: [supabase/scripts/apply_all_migrations.md](../supabase/scripts/apply_all_migrations.md).

If project creation fails with a **free-tier limit**, pause an unused active Supabase project or upgrade, then create **`rtgs-dev`**. Do not apply RTGS migrations to unrelated projects (e.g. TEAM-DDMM).

Provision roles: [backend/docs/ACCOUNT_PROVISIONING.md](../backend/docs/ACCOUNT_PROVISIONING.md).

## Smoke test

Follow [docs/SMOKE_TEST.md](./SMOKE_TEST.md) after dev env is configured.

Pre-flight (no secrets printed):

```bash
python backend/scripts/check_dev_env.py
```

Phase 7 live vs mocked results: [docs/PHASE7_VERIFICATION.md](./PHASE7_VERIFICATION.md).  
Phase 7.5 status: [docs/PHASE7_5_VERIFICATION.md](./PHASE7_5_VERIFICATION.md).

## Render CLI

```bash
render login
render workspace set   # select your workspace
# Create service from render.yaml or dashboard; set all sync:false secrets in dashboard
```

## Vercel CLI

```bash
cd frontend
vercel link    # new project e.g. rtgs-portal
vercel env add VITE_API_BASE_URL production
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production
vercel --prod
```

After deploy, set Supabase Auth **Site URL** and **Redirect URLs** to the Vercel domain; set Render `CORS_ORIGINS` to the same origin.

## CI

GitHub Actions runs backend pytest and frontend vitest/build on push/PR (SQLite mocks). Optional local browser tests: `cd frontend && npm run test:e2e:demo` (demo mode, not live Supabase). Live tests: `RTGS_LIVE_TEST=1 pytest -m live`, `E2E_LIVE=1 npm run test:e2e`.

**Production was not deployed in Phase 7.5.**
