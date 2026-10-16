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
| `backend/.env` | **MISSING** — run `bash backend/scripts/bootstrap_from_env_rtgs.sh` after creating `.env.rtgs` |
| `frontend/.env.local` | **MISSING** |
| `check_dev_env.py` | **Exit 2** until env files exist |
| `.env.rtgs` (gitignored) | **MISSING** — copy from `.env.rtgs.example` |

**Required in `.env.rtgs` (never commit):** `RTGS_DB_PASSWORD`, `RTGS_SERVICE_ROLE_KEY`, `RTGS_ANON_KEY`, optional `RTGS_JWT_SECRET`.  
See `backend/scripts/bootstrap_from_env_rtgs.sh` and [scripts/staging_deploy.md](../scripts/staging_deploy.md).

## Live tests vs mocks

| Suite | Target | Result |
|-------|--------|--------|
| Backend pytest (default) | SQLite mocks | **PASS** (30 passed; live modules skipped) |
| `test_live_workflow.py` | rtgs-dev Postgres + JWT | **NOT TESTED** — no `backend/.env` |
| `test_live_supabase.py` | Legacy placeholder | **Skipped** |
| Frontend vitest | Unit/render | **PASS** (12) |
| Playwright `test:e2e:demo` | Local demo Vite | **PASS** (3) |
| Playwright staging | Deployed URL | **NOT TESTED** |

## Render (staging)

| Item | Result |
|------|--------|
| CLI authenticated | **PASS** (`render whoami` after device login) |
| Workspace | **PASS** — `My Workspace` (`tea-db89jcgu01pc73f1ajn0`) |
| Existing RTGS service | **NONE** — only unrelated `resumefit-ai-api` in workspace |
| Git remote on repo | **MISSING** — Render deploy needs a connected remote + push or manual dashboard setup |
| Staging service URL | **BLOCKED** — create `rtgs-api` after secrets + repo |
| Health check | **NOT TESTED** |

## Vercel (staging)

| Item | Result |
|------|--------|
| CLI account | **PASS** — `harshith-debug` / `harshith-debugs-projects` |
| RTGS Vercel project | **NONE** — reuse or create e.g. `rtgs-portal` |
| Staging deploy | **BLOCKED** — needs `backend/.env` secrets flow + Render API URL |
| Staging URL | **N/A** |

## Next steps (user)

1. Copy `.env.rtgs.example` → `.env.rtgs` and fill Supabase dashboard values.
2. `bash backend/scripts/bootstrap_from_env_rtgs.sh` → `python backend/scripts/check_dev_env.py` exit 0.
3. Add a Git remote and push `main` **when you approve push**, or create `rtgs-api` manually in Render.
4. `RTGS_LIVE_TEST=1 pytest tests/test_live_workflow.py -q` (after test citizen per ACCOUNT_PROVISIONING).
5. Deploy Render `rtgs-api` — [scripts/staging_deploy.md](../scripts/staging_deploy.md).
6. `vercel deploy` from `frontend/` with `VITE_API_BASE_URL` = Render staging URL.
7. Supabase Auth Site URL + redirects = Vercel preview origin; update Render `CORS_ORIGINS`.
8. `PLAYWRIGHT_BASE_URL=<vercel-staging> E2E_LIVE=1 npm run test:e2e`.

## Security

- No secrets committed in this phase.
- Do not set `VITE_*` service role keys.
- `AUTH_DEV_BYPASS=false` for live and production paths.
