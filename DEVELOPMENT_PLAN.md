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

## Phase 4 — Frontend integration, multichannel, deploy

**Goal:** Claude UI wired to API; PWA polish; staged WhatsApp/voice; production deploy.

**Tasks:**

1. Import frontend; API client; role-based routing.
2. Citizen track + SLA warnings; officer + admin screens.
3. Email/SMS/web push providers if configured.
4. WhatsApp/voice webhooks (feature-flagged).
5. CI, Render + Vercel, smoke tests.
6. Community/municipal feeds **only if** security review passed (otherwise remain Future).

**Acceptance:**

- End-to-end: submit → assign → resolve → feedback → citizen notification.
- Staging secrets in host env only.
- Realtime or “live updates” not claimed without test evidence.

---

## Phase 2 next action (when authorized)

1. Scaffold `backend/` (FastAPI, `GET /api/v1/health`, JWT deps).
2. Create dev Supabase; apply `20251016120000_initial_schema.sql` then `20251016130000_platform_redesign_extensions.sql`; run `seed.sql`.
3. Implement **MVP** endpoints: `GET /me`, `POST/GET /grievances`, `GET /grievances/{id}/track`, `POST /grievances/{id}/analyze`, status transition route, `POST /grievances/{id}/feedback`.

Do not start Phase 2 until explicitly instructed.
