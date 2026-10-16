# RTGS Architecture

## System overview

```
┌─────────────┐     JWT (Supabase)      ┌──────────────┐
│   React     │ ───────────────────────▶│   FastAPI    │
│   (Vercel)  │     REST /api/v1        │   (Render)   │
└──────┬──────┘                         └──────┬───────┘
       │                                         │
       │  Supabase Auth + optional Realtime      │ SQL (service role / pool)
       ▼                                         ▼
┌──────────────────────────────────────────────────────────┐
│              Supabase (Postgres, Auth, Storage)           │
│  RLS for direct client reads; backend enforces authz    │
└──────────────────────────────────────────────────────────┘
       ▲
       │ optional signed uploads
       └─ Storage bucket: complaint-attachments
```

## Repository layout

```
DecodeX Final Project/          # monorepo root (RTGS)
├── frontend/                   # Claude UI → Vite React app (Phase 4)
├── backend/                    # FastAPI + AI pipeline (Phase 2+)
├── supabase/
│   ├── migrations/             # SQL source of truth for schema
│   └── seed.sql                # sample departments (dev)
├── docs/
│   └── API_CONTRACT.md         # frontend ↔ backend contract
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT_PLAN.md
└── README.md
```

## Component responsibilities

### Frontend (`frontend/`)

- Supabase Auth UI/session (email or configured providers).
- Grievance forms, tracking, officer queues, admin screens.
- Calls **FastAPI** for business logic, AI analysis, and privileged operations.
- Uses `VITE_API_BASE_URL`; sends `Authorization: Bearer <access_token>`.
- Handles loading, empty, and error states per API contract conventions.

### Backend (`backend/`)

- Validates Supabase JWT on protected routes.
- Authorizes by `profiles.role` and department/officer assignments.
- Owns grievance lifecycle, assignments, audit events, notifications.
- Runs AI pipeline (rules baseline; optional LLM module).
- Uses database connection with credentials suitable for server (pooler).
- Never exposes service role key to clients.

### Supabase

- **Auth:** single identity provider; `auth.users.id` = `profiles.id`.
- **PostgreSQL:** canonical data store; RLS on all public tables.
- **Storage:** optional attachment binaries; metadata in `attachments` table.

### AI module (backend)

- Input: grievance text, follow-up Q&A, location fields.
- Output: summary, entities, suggested category/department, urgency score, confidence, follow-up questions, `requires_human_review` flag.
- Pluggable: `AI_MODE=rules` default; optional API key for enhanced analysis.

## Authentication flow

1. Citizen/officer/admin signs in via Supabase Auth in the frontend.
2. Frontend obtains JWT `access_token` (short-lived).
3. Each API request: `Authorization: Bearer <token>`.
4. FastAPI verifies signature (JWKS from Supabase or configured JWT secret in dev), `aud`, `iss`, and expiry.
5. FastAPI loads `profiles` row by `sub` (user UUID); rejects if missing or disabled.
6. Authorization uses **database role and assignments**, not `user_metadata` from JWT.

Optional: frontend may use Supabase client for session refresh only; grievance mutations go through API for consistent validation and audit.

## Authorization model

| Action | Citizen | Officer | Admin |
|--------|---------|---------|-------|
| Create own grievance | Yes | — | — |
| Read own grievance | Yes | — | — |
| Read department assigned cases | — | Yes (scoped) | Yes |
| Update status / assign | — | Yes (scoped) | Yes |
| Manage departments | — | — | Yes |
| View audit logs | — | Limited | Yes |

Enforcement layers:

1. **FastAPI** dependency checks on every mutating route.
2. **RLS** on Postgres for defense in depth if frontend ever queries DB directly.
3. **Audit logs** for admin-sensitive and classification overrides.

## Database design (summary)

See `supabase/migrations/20251016120000_initial_schema.sql` for full DDL.

Core entities:

- `profiles` — extends auth users with role and display fields.
- `departments` — government units.
- `department_officers` — many-to-many officer ↔ department.
- `grievances` — citizen submissions with official + AI-suggested fields.
- `assignments` — officer/department responsibility over time.
- `grievance_events` — status and remark timeline.
- `ai_analyses` — versioned AI output linked to grievance.
- `attachments` — file metadata (Storage path).
- `notifications` — user inbox.
- `audit_logs` — admin and security-sensitive actions.

Reference IDs: human-readable `reference_id` (e.g. `RTGS-2026-A1B2C3`) unique index; internal UUID primary keys for joins.

## API boundaries

- Version prefix: `/api/v1`.
- JSON only; UTF-8; timestamps ISO 8601 UTC with `Z` or offset.
- Pagination: `page`, `page_size` (max 100); response includes `meta.total`, `meta.page`, `meta.page_size`.
- Errors: consistent envelope (see `docs/API_CONTRACT.md`).

Direct Supabase table access from the browser is **discouraged** for grievance writes; prefer API for audit and AI orchestration. Read-only Realtime on notifications may be added later.

## Deployment architecture

| Component | Platform | Notes |
|-----------|----------|--------|
| Frontend | Vercel | Build `frontend/`; env: Supabase public keys + API URL |
| Backend | Render | Web service; env: DATABASE_URL, JWT, service role |
| Database/Auth | Supabase | Migrations via CLI or dashboard |
| Attachments | Supabase Storage | Bucket policies aligned with RLS |

## Security notes

- No secrets in Git; use `.env.example` placeholders only.
- CORS restricted to known frontend origins.
- Rate limiting on auth and grievance creation (Phase 2).
- Attachments: virus scan / size limits (Phase 4).
- AI outputs stored with `source: rules | llm` for transparency.

## Integration assumptions for Claude UI

- Use shared TypeScript types generated from OpenAPI in Phase 4 (optional).
- Role-based routes: `/`, `/grievances`, `/grievances/:id`, `/officer`, `/admin`.
- All data fetching for grievances goes through FastAPI except Supabase Auth session.
- Display AI fields with clear “Suggested by AI” labeling; official fields editable only by officer/admin APIs.
