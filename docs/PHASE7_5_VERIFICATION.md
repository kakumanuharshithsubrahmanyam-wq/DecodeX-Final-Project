# Phase 7.5 — Integration, deployment, and verification

**Last updated:** after rtgs-dev provisioning (Oct 2026)  
**Production deploy:** Not performed.

## Supabase project (rtgs-dev)

| Field | Value |
|--------|--------|
| Name | `rtgs-dev` |
| Project reference | `fsnqpcomhtseoffwgfub` |
| Region | `ap-south-1` |
| API URL | `https://fsnqpcomhtseoffwgfub.supabase.co` |
| CLI config | `supabase/config.toml` → `project_id = fsnqpcomhtseoffwgfub` |

**Not used:** TEAM-DDMM (`zsmhricpzsybrwtajtgu`), printkiosk (`whgwknbpmrwhwktlsyge`), or other unrelated projects.

### Migration status (remote)

Applied on rtgs-dev (via Supabase MCP; forward-only):

| Remote version | Name |
|----------------|------|
| 20261016081643 | 20251016120000_initial_schema |
| 20261016081702 | 20251016120000_initial_schema_rls |
| 20261016081715 | 20251016130000_platform_redesign_extensions_p1 |
| 20261016081721 | 20251016130000_platform_redesign_extensions_p2 |
| 20261016081725 | 20251016140000_rls_role_helpers |

Phase 3 columns (`ai_analyses` provenance, `attachments.upload_status`) applied via SQL (equivalent to `20251016150000_phase3_ai_provenance.sql`).

Dev seed: **PASS** — 5 departments, 6 categories (verified row counts).

### Storage

| Check | Result |
|-------|--------|
| Bucket `complaint-attachments` exists | **PASS** |
| `public = false` | **PASS** |
| `file_size_limit = 5242880` | **PASS** |
| Live upload/download via API | **NOT TESTED** — requires local `backend/.env` with service role |

Backend signs URLs; bucket is not public.

## Local environment

| Check | Result |
|-------|--------|
| `backend/.env` | **MISSING** — run `backend/scripts/bootstrap_local_env.sh` after exporting secrets |
| `frontend/.env.local` | **MISSING** |
| `check_dev_env.py` | **Exit 2** until env files exist |

**Required user exports (never commit):** `RTGS_DB_PASSWORD`, `RTGS_SERVICE_ROLE_KEY`, `RTGS_ANON_KEY`, optional `RTGS_JWT_SECRET`.  
See `backend/scripts/bootstrap_local_env.sh`.

## Live tests vs mocks

| Suite | Target | Result |
|-------|--------|--------|
| Backend pytest (default) | SQLite mocks | **PASS** (30 passed, 1 skipped) |
| `test_live_workflow.py` | rtgs-dev Postgres + JWT | **NOT TESTED** — no `backend/.env` |
| `test_live_supabase.py` | Legacy placeholder | **Skipped** |
| Frontend vitest | Unit/render | **PASS** (12) |
| Playwright `test:e2e:demo` | Local demo Vite | **PASS** (3) |
| Playwright staging | Deployed URL | **NOT TESTED** |

## Render (staging)

| Item | Result |
|------|--------|
| CLI authenticated | **BLOCKED** — run `render login` |
| Staging service URL | **N/A** |
| Health check | **NOT TESTED** |

## Vercel (staging)

| Item | Result |
|------|--------|
| CLI account | `harshith-debug` — **confirm with user before RTGS deploy** |
| Staging deploy | **NOT TESTED** — blocked on env + account confirmation |
| Staging URL | **N/A** |

## Next steps (user)

1. Export secrets and run `bash backend/scripts/bootstrap_local_env.sh`.
2. `python backend/scripts/check_dev_env.py` → exit 0.
3. `cd backend && uvicorn app.main:app --reload` and `RTGS_LIVE_TEST=1 pytest tests/test_live_workflow.py -q`.
4. Supabase Auth: set Site URL / redirects when Vercel staging URL exists.
5. `render login` → deploy `rtgs-api` staging with dashboard secrets.
6. Confirm Vercel team → deploy `frontend/` with `VITE_API_BASE_URL` = Render staging URL.
7. `PLAYWRIGHT_BASE_URL=<vercel-staging> E2E_LIVE=1 npm run test:e2e`.

## Security

- No secrets committed in this phase.
- Do not set `VITE_*` service role keys.
- `AUTH_DEV_BYPASS=false` for live and production paths.
