# Phase 7.5 — Integration, deployment, and verification

**Base commit:** `c96352f` (Phase 7)  
**Production deploy:** Not performed.  
**Live Supabase rtgs-dev:** **BLOCKED** (see below).

## 1. Implementation completed (this phase)

| Item | Status |
|------|--------|
| Playwright browser E2E (demo mode, dev server) | **PASS** — `npm run test:e2e:demo` |
| Playwright live E2E scaffold | **NOT TESTED** — requires `E2E_LIVE=1` + Supabase |
| `check_dev_env.py` production safety checks | **PASS** — extended |
| Storage bucket SQL script | Added `supabase/scripts/create_storage_bucket.sql` |
| Migration runbook | Added `supabase/scripts/apply_all_migrations.md` |
| Deployment docs | Updated `DEPLOYMENT.md`, `SMOKE_TEST.md`, `README.md` |

## 2. Supabase project and migration status

| Check | Result | Evidence |
|-------|--------|----------|
| Create dedicated `rtgs-dev` project | **BLOCKED** | Supabase API: org free-tier limit (2 active projects: TEAM-DDMM, printkiosk) |
| Supabase CLI installed locally | **FAIL** | `supabase` not on PATH |
| Supabase MCP authenticated | **PASS** | Organizations listed |
| Repurpose unrelated project | **Not done** | TEAM-DDMM has separate schema; inactive projects timed out |
| Migrations applied remotely | **NOT TESTED** | No RTGS dev project |
| Local migration files (4) | **PASS** | Verified in repo |

**Required user action:** In [Supabase dashboard](https://supabase.com/dashboard), **pause** an unused active project or **upgrade**, then create **`rtgs-dev`** in `ap-south-1`. Do **not** apply RTGS migrations to TEAM-DDMM or printkiosk.

After project exists:

1. `supabase link --project-ref <ref>`
2. `supabase db push`
3. Run seed + storage scripts as documented
4. Copy keys into `backend/.env` and `frontend/.env.local` (never commit)

## 3. Authentication, roles, and RLS

| Check | Live dev | Mocked |
|-------|----------|--------|
| Signup/login/session | **BLOCKED** | Demo mode dev-only |
| JWT + `/api/v1/me` | **BLOCKED** | **PASS** pytest |
| Citizen isolation | **BLOCKED** | **PASS** |
| Officer/moderator/admin | **BLOCKED** | **PASS** (incl. moderator 403) |
| Production `AUTH_DEV_BYPASS` | N/A | **PASS** startup test |
| RLS in migrations | **NOT TESTED** on remote | **PASS** policies in SQL files |

RLS is defined in migrations; backend uses service role for signed URLs with app-level checks (`permissions.py`, `can_read_grievance`).

## 4. Storage and attachments

| Check | Result |
|-------|--------|
| Bucket `complaint-attachments` on dev | **NOT TESTED** |
| Upload URL / complete / download live | **NOT TESTED** |
| MIME/size validation | **PASS** unit tests |
| Mock upload URL flow | **PASS** `test_attachment_upload_mock` |

## 5. Citizen-to-officer workflow

All **live** steps **BLOCKED** without database and Auth. **Mocked** API workflow **PASS** (pytest suite).

## 6. Automated test results

| Suite | Target | Result |
|-------|--------|--------|
| Backend pytest | SQLite mocks | **30 passed**, 1 skipped |
| Frontend vitest | Unit/render | **12 passed** |
| Frontend `npm run build` | Production bundle | **PASS** (run locally in phase) |
| Playwright `test:e2e:demo` | Local Vite + `VITE_DEMO_MODE` | **3 passed** (after dev-server fix) |
| Playwright `live.spec.ts` | Remote | **Skipped** |
| CI (GitHub Actions) | Mocks | Unchanged |

## 7. Render deployment

| Check | Result |
|-------|--------|
| `render.yaml` present | **PASS** |
| Render CLI authenticated | **BLOCKED** — `render login` required |
| Service deployed | **NOT TESTED** |
| Health URL | **N/A** |

Configure after Supabase: set `DATABASE_URL`, `SUPABASE_*`, `JWT_ISSUER`, `CORS_ORIGINS` (Vercel URL), `AUTH_DEV_BYPASS=false`, `APP_ENV=production`.

## 8. Vercel deployment

| Check | Result |
|-------|--------|
| Vercel CLI authenticated | **PASS** — account `harshith-debug` |
| RTGS-specific production deploy | **NOT TESTED** — no backend URL / Supabase env for integrated build |
| Existing unrelated `frontend` project on Vercel | Not used (wrong app) |

Deploy when ready:

```bash
cd frontend
vercel --prod   # set VITE_API_BASE_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY in project settings
```

**Do not** set `VITE_DEMO_MODE=true` on Vercel production.

## 9. Environment variables (names only)

**Backend (Render / local):** `APP_ENV`, `AUTH_DEV_BYPASS`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_ISSUER`, `JWT_AUDIENCE`, `CORS_ORIGINS`, `AI_MODE`, `SUPABASE_STORAGE_BUCKET`, `SIGNED_URL_TTL_SECONDS`, `ATTACHMENT_MAX_BYTES`, `ATTACHMENT_ALLOWED_CONTENT_TYPES`

**Frontend (Vercel / local):** `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, optional `VITE_APP_ENV` — never `VITE_DEMO_MODE` in production

**Supabase Auth dashboard:** Site URL, redirect URLs for Vercel + `http://localhost:5173`

## 10. Security review

| Item | Result |
|------|--------|
| Secrets in git | **PASS** — `.env` gitignored; no `.env` committed |
| Service role in frontend | **PASS** — not in Vite vars |
| Prod auth bypass | **PASS** — enforced in `main.py` + checker |
| Moderator grievance access | **PASS** — mocked 403 |
| Anonymous private grievance access | **PASS** — auth required in app |

**Remaining risk:** Live RLS/storage policies unverified until rtgs-dev exists.

## 11. Commits and working tree

Phase 7.5 commit(s) to follow this document. Untracked: `frontend/rtgs-frontend-new.zip`, `frontend/scripts/i18n-6b.mjs`.

## 12. Outstanding user actions

1. **Free Supabase slot:** Pause or upgrade a project → create **`rtgs-dev`**.
2. **Local env:** Copy example env files; fill from Supabase dashboard.
3. **Migrations + bucket:** Follow `supabase/scripts/apply_all_migrations.md`.
4. **Provision test users:** `backend/docs/ACCOUNT_PROVISIONING.md`.
5. **Render:** `render login`, create/link `rtgs-api`, set env vars, deploy.
6. **Vercel:** New project or link repo root `frontend`, set public env vars, deploy.
7. **CORS + Auth redirects:** Wire actual Render/Vercel URLs.
8. Re-run `check_dev_env.py`, manual SMOKE_TEST, `E2E_LIVE=1` when ready.
