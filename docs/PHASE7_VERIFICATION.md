# Phase 7 — Development Supabase integration and verification

**Base commit:** `3f7ffbc` (Phase 6B)  
**Production:** Not deployed or accessed in this phase.

## 1. Development environment status

| Item | Status |
|------|--------|
| `backend/.env` | **Not present** in this workspace |
| `frontend/.env.local` | **Not present** in this workspace |
| `supabase/config.toml` `project_id` | Placeholder `YOUR_RTGS_DEV_PROJECT_REF` (not linked) |
| Supabase CLI link / remote project | **Not verified** (no local credentials) |
| `python backend/scripts/check_dev_env.py` | Exit **2** — env files missing |

**Conclusion:** A dedicated RTGS **development Supabase project is not configured in this checkout.** All live Auth, Postgres, Storage, and browser E2E steps are **blocked** until dev credentials are added locally (never committed).

### Manual setup (when you have a dev project)

1. Copy `backend/.env.example` → `backend/.env` and `frontend/.env.example` → `frontend/.env.local`; fill values in the Supabase dashboard only.
2. Link CLI: `supabase link --project-ref <RTGS_DEV_REF>` (dev project only).
3. Inspect migrations: `supabase migration list` — apply **forward-only** pending: `supabase db push` (do not reset DB).
4. Seed (dev empty DB only): `psql "$DATABASE_URL" -f supabase/seed.sql` after reviewing `supabase/seed.sql`.
5. Storage: create private bucket `complaint-attachments` per [supabase/storage/complaint-attachments-policy.md](../supabase/storage/complaint-attachments-policy.md).
6. Users/roles: [backend/docs/ACCOUNT_PROVISIONING.md](../backend/docs/ACCOUNT_PROVISIONING.md) — citizens via Auth signup; staff via SQL/service role.
7. Optional live pytest: `RTGS_LIVE_TEST=1 pytest -m live` (see [backend/tests/test_live_supabase.py](../backend/tests/test_live_supabase.py)).
8. Optional API smoke with bypass: `AUTH_DEV_BYPASS=true` + Postgres `DATABASE_URL` → `python backend/scripts/smoke_dev_bypass.py`.

Migration files in repo (apply in order):

1. `20251016120000_initial_schema.sql`
2. `20251016130000_platform_redesign_extensions.sql`
3. `20251016140000_rls_role_helpers.sql`
4. `20251016150000_phase3_ai_provenance.sql`

## 2. Authentication and authorization

| Check | Live dev | Mocked (pytest / SQLite) |
|-------|----------|---------------------------|
| Citizen signup + profile `citizen` | **Blocked** | Register flow uses `signUpCitizen`; role from DB trigger (documented) |
| Login / logout / session refresh | **Blocked** | N/A |
| `GET /api/v1/me` + permissions | **Blocked** | **Passed** — `test_me_citizen`, `test_me_community_moderator_permissions` |
| Citizen cannot read other citizen grievance | **Blocked** | **Passed** — `test_citizen_cannot_see_other_grievance` |
| Officer assign + transition | **Blocked** | **Passed** — `test_officer_assignment_and_transition` |
| Platform admin analytics | **Blocked** | **Passed** — `test_analytics_admin` |
| Community moderator no private grievance access | **Blocked** | **Passed** — `test_community_moderator_cannot_read_grievance` (403) |
| Invalid token without dev bypass | **Blocked** | **Passed** — `test_unauthorized_without_bypass` (401) |
| Production blocks `AUTH_DEV_BYPASS` | N/A | **Passed** — `test_startup_blocks_production_bypass` |
| Client-supplied privileged roles | **Blocked** | Roles from `profiles` only (`resolve_user_from_token`); provisioning doc forbids metadata roles |
| Frontend route guards | N/A | **Unit** — `frontend/src/auth/roles.test.ts` (UX only; backend authoritative) |

## 3. End-to-end grievance workflow (synthetic dev data)

| Step | Live dev | Mocked API tests |
|------|----------|------------------|
| 1. Citizen signs in | **Blocked** | N/A (bypass simulates user id) |
| 2. Submit incomplete complaint | **Blocked** | **Passed** — create grievance |
| 3. AI completeness / follow-up | **Blocked** | **Passed** — `test_analyze_endpoint` (`follow_up_questions`) |
| 4. Additional information | **Blocked** | Partial — API supports updates; not re-run live |
| 5. Persisted reference ID | **Blocked** | **Passed** — `RTGS-` prefix in create |
| 6. Citizen view + history | **Blocked** | **Passed** — list/detail via same citizen |
| 7. Officer assign | **Blocked** | **Passed** |
| 8. Valid status transition | **Blocked** | **Passed** |
| 9. Events / notifications | **Blocked** | **Passed** — `test_notifications_list` |
| 10. Feedback when eligible | **Blocked** | **Passed** — `test_feedback_after_resolve` |
| 11. Second citizen denied | **Blocked** | **Passed** |
| 12. Reopen where permitted | **Blocked** | **Passed** — `test_reopen_citizen` |
| 13. Analytics from persisted data | **Blocked** | **Passed** — admin overview test |

## 4. Storage

| Check | Live dev | Mocked |
|-------|----------|--------|
| Upload URL | **Blocked** | **Passed** — `test_attachment_upload_mock` (mock URL) |
| PUT file + complete | **Blocked** | Not exercised against real Storage |
| Download URL authorized | **Blocked** | Not run live |
| Unauthorized download | **Blocked** | Not run live |
| Invalid type / size | **Blocked** | **Passed** — `test_validate_upload_rejects_type` |
| Failed upload not shown as success | **Blocked** | Frontend uses API errors in live submit path |

No virus scanning is implemented or claimed.

## 5. Frontend integration and localization

| Check | Result |
|-------|--------|
| `npm test` | **12 passed** (roles, i18n parity, locale switch, portal workflow + open dialog) |
| `npm run build` | **Pass** |
| Live citizen journey EN/TE in browser | **Blocked** (no Supabase + API env) |
| Officer/admin routing vs `/api/v1/me` | **Blocked** live; route map in `roles.ts` matches backend roles |
| Demo vs live data separation | **Code verified** — `canUseLiveApi`, `GrievanceContext` modes, `DataSourceNotice` |

Remaining hardcoded UI (documented): demo community post bodies, local `classify()` reason strings, GHMC department names, map landmark labels, user complaint text from API.

## 6. Demo and unsupported features (code review)

| Feature | Status |
|---------|--------|
| Demo records vs live API | Isolated when `VITE_DEMO_MODE` or no session/API |
| SLA local editor | `DataSourceNotice variant="sla"`; localStorage only |
| Chatbot | Labeled `portal.chat.subtitle` / `portal.dataSource.chatbot` |
| Illustrative admin trend chart | `DataSourceNotice variant="illustrativeChart"` when not live analytics |
| Community posting | `portal.dataSource.community`; localStorage |
| Anonymous public tracking | Not implemented; track requires grievance in user’s allowed set / sign-in notice |

## 7. Automated test summary

| Suite | Type | Result |
|-------|------|--------|
| `backend` pytest (default) | Unit + mocked integration (SQLite) | **30 passed**, **1 skipped** (`test_live_supabase`) |
| `pytest -m live` | Live Postgres | **Skipped** (`RTGS_LIVE_TEST` not set) |
| `frontend` vitest | Unit + render | **12 passed** |
| `frontend` `npm run build` | Production build | **Pass** |
| GitHub Actions CI | Same as above | Configured in `.github/workflows/ci.yml` |
| Browser E2E (Playwright/Cypress) | — | **Not present** in repository |

## 8. Remaining blockers

1. Create/configure **dedicated RTGS dev Supabase** project and local env files.
2. Run `supabase migration list` / `db push` on that project only.
3. Create Storage bucket and policies.
4. Provision test users per ACCOUNT_PROVISIONING.md.
5. Execute manual checklist in [SMOKE_TEST.md](./SMOKE_TEST.md) and record pass/fail.
6. Optionally implement real cases in `test_live_supabase.py` once `RTGS_LIVE_TEST=1`.

**Explicit:** Production was not deployed, accessed, or migrated in Phase 7.
