# RTGS Development Plan (Accelerated, Four Phases)

## Workflow split

| Owner | Responsibility |
|-------|----------------|
| **Claude** | React + TypeScript + Vite + Tailwind + shadcn/ui — citizen, officer, admin UX |
| **Cursor** | Git, FastAPI, Supabase, AI pipeline, integrations, tests, deployment |

Single repo; contract: [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

---

## Phase 1 — Foundation and redesign ✅

**Goal:** Product vision, architecture, data model plan, API contract, integration interfaces, migrations as SQL drafts (not applied live).

**Deliverables:**

- Updated PROJECT_SPEC, ARCHITECTURE, DEVELOPMENT_PLAN, README
- docs: API_CONTRACT, FRONTEND_INTEGRATION, FEATURE_MATRIX, DATA_MODEL, INTEGRATIONS
- Migrations: initial + `20251016130000_platform_redesign_extensions.sql`
- Env examples; `.gitignore`

**Acceptance:** Documented MVP vs deferred; no full app implementation; Git history preserved.

---

## Phase 2 — Backend core + database (MVP spine)

**Goal:** Runnable API, applied migrations on dev Supabase, auth, grievance CRUD, lifecycle, SLA hooks, in-app notifications.

**Tasks:**

1. FastAPI scaffold: settings, health, JWT middleware, error envelope.
2. Apply migrations in order; run seed (departments, categories, SLA policies).
3. Implement MVP endpoints (see API contract tags): `/me`, grievances CRUD, track/history, status transitions, assignments, categories list, SLA on grievance, notifications list, feedback submit.
4. State machine tests; permission tests per role.
5. Rules-based AI: analyze + follow-up (minimal).
6. RLS policy completion for new tables; document service-role usage boundaries.

**Acceptance:**

- Citizen submit → reference ID → timeline events → SLA due dates visible.
- Officer cannot read unrelated citizen grievances.
- Invalid status transition returns 409.
- No endpoint marked Future is required to pass MVP demo.

**Dependencies:** Dev Supabase project; `.env` from examples.

---

## Phase 3 — AI depth, officer/admin ops, delivery prep

**Goal:** Richer AI, department admin flows, attachment pipeline, notification router stubs, duplicate detection prep.

**Tasks:**

1. AI pipeline steps 2–11 (language, duplicates, image adapter interface).
2. Department administrator endpoints and queues.
3. Attachment signed URLs + Storage policies.
4. Reopen/review; escalation automation on SLA breach.
5. Analytics MVP dashboards API.
6. Optional LLM provider behind feature flag.
7. Evaluation harness (Telugu/English fixtures).

**Acceptance:**

- Low-confidence analyses flagged; officer override audited.
- Post-resolution feedback enforced once per citizen.
- Image upload works; analysis advisory when provider configured.

---

## Phase 4 — Frontend integration + deployment readiness (partial ✅)

**Completed:**

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), [docs/SMOKE_TEST.md](docs/SMOKE_TEST.md), [render.yaml](render.yaml), CI workflow
- Shared `frontend/src/lib/` API client (no Claude UI pages)
- Production startup guard for `AUTH_DEV_BYPASS`
- Live test placeholder (`RTGS_LIVE_TEST=1`)

**Blocked:**

- Claude Vite app import and Vercel deploy
- Live Supabase E2E on dedicated RTGS dev project (configure `backend/.env` + link Supabase CLI)

**Remaining:** Import UI → wire lib → run manual smoke on dev → staging deploy (not production).

---

## Post-Phase 4 next action

1. Claude: deliver full Vite app into `frontend/` preserving design.
2. Cursor/user: create **RTGS-only** Supabase dev project; `supabase link` + `db push` + bucket + roles.
3. Configure Render/Vercel staging; run [docs/SMOKE_TEST.md](docs/SMOKE_TEST.md).
