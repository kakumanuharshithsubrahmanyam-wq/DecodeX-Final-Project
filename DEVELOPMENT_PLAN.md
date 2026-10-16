# RTGS Development Plan (Accelerated)

## Workflow split

| Owner | Responsibility |
|-------|----------------|
| **Claude** | React + TypeScript + Vite + Tailwind + shadcn/ui — citizen, officer, and admin UI/UX. |
| **Cursor** | Git, FastAPI backend, Supabase schema/RLS, AI pipeline, APIs, tests, deployment config. |

The Claude-generated frontend is imported into `frontend/` and wired to the API contract in `docs/API_CONTRACT.md`.

---

## Phase 1 — Foundation (current)

**Goal:** Repository structure, Git, integration blueprint, database blueprint, environment templates, architecture docs.

**Deliverables:**

- Monorepo layout (`frontend/`, `backend/`, `supabase/`, `docs/`).
- `.gitignore`, README, PROJECT_SPEC, ARCHITECTURE, DEVELOPMENT_PLAN.
- API contract and Supabase draft migration (not applied to live project).
- `.env.example` files for frontend and backend.

**Acceptance:**

- No secrets in Git; initial commit if safe.
- Clear Phase 2 entry criteria documented.

**Status:** Complete when Phase 1 report is delivered.

---

## Phase 2 — Backend core + database

**Goal:** Runnable FastAPI app, Supabase migration applied (dev project), auth middleware, core grievance CRUD.

**Tasks:**

1. Initialize `backend/` (FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic or Supabase migrations as source of truth).
2. Apply `supabase/migrations/*` to dev Supabase; seed departments.
3. Implement JWT validation (Supabase JWKS or JWT secret per environment).
4. Implement endpoints: auth profile, grievances CRUD, events, assignments (minimal).
5. RLS policies aligned with FastAPI service role vs user-scoped client usage.
6. Pytest for auth and grievance permissions.

**Acceptance:**

- Citizen can create/list own grievances via API with valid JWT.
- Officer cannot access unassigned grievances outside department rules.
- OpenAPI matches `docs/API_CONTRACT.md` (version noted in changelog if drift).

**Dependencies:** Supabase dev project, env files from examples.

---

## Phase 3 — AI pipeline + officer/admin flows

**Goal:** Analysis pipeline, follow-ups, recommendations, officer status workflow, notifications.

**Tasks:**

1. Modular `ai/` package: rules engine + optional LLM adapter.
2. Endpoints: analyze, follow-up answers, re-analyze, recommendations.
3. Persist `ai_analyses`; link to grievances and events.
4. Officer assignment and status transition rules with audit logs.
5. In-app notifications on key transitions.
6. Integration tests for analysis idempotency and human-review flags.

**Acceptance:**

- New grievance triggers analysis record with confidence and explainable urgency.
- Low-confidence cases flagged for officer review in API response.
- Status history complete and ordered.

---

## Phase 4 — Frontend integration + deployment

**Goal:** Import Claude UI, connect to API, deploy to Vercel + Render.

**Tasks:**

1. Merge Claude frontend into `frontend/`; align env vars and API client.
2. Supabase Auth on client; attach JWT to FastAPI requests.
3. Storage upload flow for attachments (signed URLs or backend proxy).
4. Admin analytics endpoints and dashboard wiring.
5. CI (lint/test), Render `render.yaml` or equivalent, Vercel project settings.
6. Smoke tests on staging.

**Acceptance:**

- End-to-end demo: citizen submit → officer resolve → citizen notified.
- Production secrets only in host env, not repository.
- Health checks and CORS configured.

---

## Phase 2 next action (immediate)

1. Scaffold FastAPI in `backend/` with health check and settings module.
2. Create Supabase dev project and apply initial migration.
3. Implement `GET /api/v1/me` and `POST /api/v1/grievances` per API contract.

Stop all implementation at Phase 1 until explicitly instructed to begin Phase 2.
