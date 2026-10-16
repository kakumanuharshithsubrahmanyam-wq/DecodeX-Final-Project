# RTGS Architecture

Citizen-centric urban governance platform: grievance redressal, SLA-aware operations, modular AI, and staged multichannel integrations.

## System context

```
                    ┌─────────────────────────────────────────┐
                    │           Intake (staged)                │
                    │  Web/PWA │ Chatbot │ WhatsApp │ Voice   │
                    └────────────────────┬────────────────────┘
                                         │
┌─────────────┐   JWT + REST    ┌────────▼─────────┐   ┌──────────────┐
│ React (Vite)│ ───────────────▶│ FastAPI (Render) │──▶│ AI pipeline  │
│  (Vercel)   │                 │  /api/v1         │   │ rules + opt  │
└──────┬──────┘                 └────────┬─────────┘   └──────────────┘
       │ Supabase Auth session          │ SQL / Storage
       ▼                                  ▼
┌──────────────────────────────────────────────────────────────┐
│ Supabase: PostgreSQL (RLS), Auth, Storage, Realtime (future)  │
└──────────────────────────────────────────────────────────────┘
       ▲
       └── Notification providers (email/SMS/WhatsApp) — Next/Future
```

## Repository layout

```
├── frontend/          # Claude UI (React + Vite + Tailwind)
├── backend/           # FastAPI, AI, integrations, workers (Phase 2+)
├── supabase/migrations/
├── docs/              # API, data model, features, integrations
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
└── DEVELOPMENT_PLAN.md
```

## Component responsibilities

### Frontend

- Responsive web first; PWA-ready layout (install optional later).
- Supabase Auth for session; FastAPI for grievances, AI, admin, notifications.
- Citizen timeline, officer queues, admin analytics (per [docs/API_CONTRACT.md](docs/API_CONTRACT.md)).
- Distinct UI treatment: **AI suggestion** vs **official** vs **general guidance**.
- Polling for timeline updates in MVP; Realtime subscription only after tested (Future).

### Backend

- Supabase JWT verification on protected routes.
- Role and assignment checks on every mutating operation.
- Grievance state machine enforcement ([docs/DATA_MODEL.md](docs/DATA_MODEL.md)).
- SLA computation on create/assign/priority change.
- Notification orchestration with dedupe and preferences.
- Integration webhooks (WhatsApp/voice) behind feature flags (Future).
- AI pipeline orchestration; no mandatory paid LLM.

### Database (Supabase PostgreSQL)

- Canonical records: grievances, events (timeline source of truth), assignments, SLA, feedback.
- RLS enabled on all public tables; policies align with roles.
- Service role used **narrowly** for system tasks (webhook intake, outbound delivery) with explicit authorization logic — not as a blanket bypass for user APIs.

## Authentication and authorization

1. User signs in via Supabase Auth (frontend).
2. API requests include `Authorization: Bearer <access_token>`.
3. FastAPI validates JWT (`iss`, `aud`, expiry, signature via JWKS or dev secret).
4. Load `profiles` by `sub`; deny inactive users.
5. Authorize using `profiles.role`, `department_officers`, and assignment rows — **never** JWT `user_metadata` for privileges.

| Role | Scope |
|------|--------|
| Citizen | Own grievances, feedback, preferences |
| Officer | Assigned + department policy |
| Department administrator | Department queues and assignments (Next) |
| Platform administrator | Global config, analytics, audit |
| Community moderator | Community resources only (Future) |

Legacy enum value `administrator` ≡ `platform_administrator` in application code.

## Grievance lifecycle (backend)

Statuses and transitions are defined in [docs/DATA_MODEL.md](docs/DATA_MODEL.md). Each transition writes a `grievance_events` row. API maps legacy `in_review` ↔ `under_review` for compatibility.

## AI architecture

Modular pipeline (single orchestrator, swappable providers):

| Step | Output |
|------|--------|
| 1. Intake normalization | Clean text, channel metadata |
| 2. Language detection | `en` / `te` (Next) |
| 3. Completeness check | Missing fields list |
| 4. Follow-up questions | Structured Q&A |
| 5. Information extraction | Locations, entities (JSON) |
| 6. Summarization | Neutral summary |
| 7. Category/dept recommendation | Taxonomy codes + dept id |
| 8. Priority assessment | Score, label, explanation |
| 9. Duplicate/related detection | Candidate links (Next) |
| 10. Optional image analysis | Advisory labels, OCR (Next) |
| 11. Confidence + explanation | `requires_human_review` |
| 12. Human actions | Officer/admin only via workflow APIs |

Python interfaces (Phase 2+): `TextAnalysisProvider`, `ImageAnalysisProvider`, `LanguageDetector`, `SimilarityProvider`, `TranscriptionProvider`.

**Evaluation plan (Phase 3):** curated Telugu/English samples, vague text, overlapping categories, urgent keywords — measure override rate and review flags; no accuracy claims without measured results.

**Chatbot tools (Next):** read own grievance status, create **draft** grievance, list categories — each tool gated by auth; confirm before final submit.

## Multichannel intake

All channels converge on `GrievanceService.create_from_intake()` with `intake_channel` and optional `intake_external_id`. See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).

## Notifications

- MVP: in-app rows on submission, assignment, status change, needs_information, SLA breach.
- Next: router to email/SMS/web push with delivery attempts.
- Preferences and quiet hours in `notification_preferences`.
- Emergency: authorized content only.

## Privacy and security

| Topic | Approach |
|-------|----------|
| Secrets | Env only; never in frontend or Git |
| Service role | Server-only; not for citizen-facing routes |
| RLS | Complement API; fix gaps before direct client reads |
| Attachments | Signed URLs; short TTL; role-scoped |
| Location | Avoid publishing precise coords in public/community APIs |
| Analytics | Aggregates only; k-anonymity for small wards (TBD threshold) |
| Prompt injection | Sanitize display; system prompts isolated; no tool exec from raw complaint text alone |
| Audit | `audit_logs` for admin/role changes and classification overrides |
| Retention | Documented in DATA_MODEL; erasure requests via admin process (Phase 4) |
| Rate limiting | Auth, create grievance, chat (Phase 2+) |

## Deployment

| Layer | Host |
|-------|------|
| Frontend | Vercel |
| API | Render |
| DB/Auth/Storage | Supabase |

## API boundary

- Prefix `/api/v1`; JSON; ISO 8601 timestamps.
- Endpoints tagged MVP / Next / Future in [docs/API_CONTRACT.md](docs/API_CONTRACT.md).
- OpenAPI generated from FastAPI in Phase 2; contract is normative for Claude UI until then.

## Frontend integration

See [docs/FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md).
