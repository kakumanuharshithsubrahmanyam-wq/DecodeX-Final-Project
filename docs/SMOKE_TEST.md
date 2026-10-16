# RTGS End-to-End Smoke Test (development only)

Run only against a **dedicated dev** Supabase project and dev/staging API. Do not use production citizen data.

## Environment pre-check

```bash
python backend/scripts/check_dev_env.py
```

Reports whether `backend/.env` and `frontend/.env.local` exist and required keys are set (values are never printed). Exit code `0` means configured; `2` means live E2E is blocked.

Full Phase 7 matrix (live vs mocked): [PHASE7_VERIFICATION.md](PHASE7_VERIFICATION.md).  
Phase 7.5 deployment/integration: [PHASE7_5_VERIFICATION.md](PHASE7_5_VERIFICATION.md).

## Browser E2E (demo — not live Supabase)

```bash
cd frontend && npm run test:e2e:demo
```

Uses Vite dev server with `VITE_DEMO_MODE=true`. Live browser tests: `E2E_LIVE=1 npm run test:e2e` after configuring Supabase test accounts.

## Automated (API + dev bypass — not live Supabase Auth)

```bash
cd backend && source .venv/bin/activate && pytest -q
```

This validates grievance flows with SQLite mocks (30+ tests). **This is not a live Supabase smoke test.**

## Optional live script

Requires `backend/.env` with real `DATABASE_URL` and `AUTH_DEV_BYPASS=true` plus seeded profiles:

```bash
cd backend && source .venv/bin/activate
python scripts/smoke_dev_bypass.py
```

Exit code 0 only if health + create grievance succeed against configured Postgres.

## Manual E2E (real Supabase Auth) — checklist

1. **Citizen sign-in** via Supabase Auth in the frontend (`/login`).
2. **Submit grievance** with vague text → receive reference ID; verify `needs_information` or follow-up questions from `POST .../analyze`.
3. **Submit additional info** → status moves toward review.
4. **Attachment** (optional): upload-url → PUT to signed URL → complete → download-url as same user.
5. **Officer sign-in** (role provisioned in DB) → list dept/assigned queue → assign → transition `in_progress` → `resolved` → `closed`.
6. **Citizen feedback** on closed/resolved grievance.
7. **Notifications** list shows submission/status events.
8. **Negative tests:**
   - Citizen B cannot `GET` citizen A's grievance (403/404).
   - Expired/invalid JWT → 401.
   - Community moderator (if provisioned) cannot access private grievance APIs.

Record results in your run log; do not claim live verification unless each step was executed against dev.

## Phase 7.5 status (this repo checkout)

| Area | Result |
|------|--------|
| Supabase `rtgs-dev` project | **BLOCKED** — org free active project limit (2/2) |
| Live Auth / Postgres / Storage | **NOT TESTED** |
| Playwright demo E2E | **3 tests** — `npm run test:e2e:demo` |
| Render deploy | **BLOCKED** — `render login` required |
| Vercel RTGS deploy | **NOT TESTED** — needs Supabase + API URLs |
| Production deploy | **Not performed** |

## Phase 7 status (this repo checkout)

| Area | Result |
|------|--------|
| Dev Supabase project configured locally | **No** — `backend/.env` and `frontend/.env.local` absent |
| Migrations applied to dev Postgres | **Not run** (no linked project in workspace) |
| Live Auth / workflow / Storage E2E | **Blocked** — see [PHASE7_VERIFICATION.md](PHASE7_VERIFICATION.md) |
| Mocked backend pytest | **30 passed**, 1 skipped (`test_live_supabase`) |
| Frontend tests + build | **12 passed**; `npm run build` OK |
| Browser automation E2E | **Not in repo** |
| Production deploy | **Not performed** |

## Phase 6B status (this repo checkout)

| Area | Result |
|------|--------|
| Design archive `rtgs-frontend-new.zip` | **Present** — extracted to `design/reference/rtgs/`; see [PHASE6_DESIGN_ARCHIVE.md](PHASE6_DESIGN_ARCHIVE.md) |
| Frontend tests | 12 passed (roles, i18n parity, locale switch, portal workflow render) |
| Frontend build | `npm run build` |
| Backend pytest | 30 passed, 1 skipped (Phase 7) |
| Live Supabase Auth / Postgres / Storage | **Pending** — no committed `.env`; use dev credentials per setup below |

## Phase 5 status (this repo checkout)

| Area | Result |
|------|--------|
| Frontend unit tests | `npm test` — role mapping + i18n parity |
| Frontend build | `npm run build` |
| Backend pytest | 27 passed, 1 skipped (live Supabase test) |
| Live Supabase Auth / Storage / Postgres | **Pending** — only `.env.example` present; copy dev credentials to `backend/.env` and `frontend/.env.local` |

Setup for live dev verification:

1. Create or use a dedicated Supabase dev project; run migrations from `supabase/migrations/`.
2. `frontend/.env.local`: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_BASE_URL`; do **not** set `VITE_DEMO_MODE=true` in production builds.
3. `backend/.env`: `DATABASE_URL`, `SUPABASE_JWT_SECRET`, optional Storage keys for attachment smoke tests.
4. Run the manual checklist above and note which steps used real services vs mocks.

## Attachment verification

| Step | Expected |
|------|----------|
| Oversized file | 400 VALIDATION_ERROR |
| Wrong MIME type | 400 |
| Upload without auth | 401 |
| Download other citizen's file | 403/404 |
| Success | `upload_status: completed` only after `complete` endpoint |

Mock Storage URLs in local dev without `SUPABASE_SERVICE_ROLE_KEY` do **not** prove real Storage uploads.
