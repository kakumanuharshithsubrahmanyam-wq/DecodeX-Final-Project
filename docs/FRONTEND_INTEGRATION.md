# Frontend Integration Guide (Claude UI)

RTGS: citizen-centric urban governance — responsive web first, API-driven data, Supabase Auth only for identity.

## Stack and placement

- React 18+, TypeScript, Vite, Tailwind CSS, shadcn/ui.
- Source under `frontend/` (standard Vite layout).
- **Current repo state:** Supplied UI lives in `frontend/src/RtgsPortal.tsx` with auth/i18n/API layers in `src/auth`, `src/data`, `src/lib`, `src/i18n`. Community posts remain local-only until a backend community API exists.

- Mobile-friendly layouts; PWA manifest optional in Phase 4 — **not** a native app in MVP.

## Environment

From `frontend/.env.example`:

- `VITE_API_BASE_URL`
- `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (publishable key only)

## Authentication and roles

1. Supabase Auth for register/login/session refresh.
2. Attach `Bearer` token to all API calls.
3. `GET /api/v1/me` → `role` and `permissions` for route guards.

Roles: `citizen`, `officer`, `department_administrator`, `platform_administrator`, `community_moderator`.

Treat legacy `administrator` as `platform_administrator` in UI labels.

**Phase 5 mapping:** `frontend/src/auth/roles.ts` maps API roles to workspace kinds (`citizen`, `officer`, `dept_admin`, `platform_admin`, `moderator`) and applies route allowlists. `/api/v1/me` is authoritative; guards wait for `profileStatus === 'ready'`. Display labels for status/priority/category use `src/i18n/displayLabels.ts` while API payloads keep canonical enum values.

**Localization:** portal copy lives under `portal.*` in `src/i18n/en.ts` / `te.ts` (sourced from `portal-en.ts` / `portal-te.ts`). Enum display is translated; citizen-submitted text is not.

**Data honesty:** `DataSourceNotice` marks demo, illustrative charts, local-only community/SLA, and the scripted help assistant. Live admin totals use `GET /api/v1/analytics/overview` when `liveApi` is true (no monthly time series from API — trend chart stays illustrative).

## Data access rules

| Concern | Source |
|---------|--------|
| Grievances, AI, SLA, feedback, admin | FastAPI |
| Session | Supabase Auth |
| Realtime timeline | **Not MVP** — poll track endpoint or refresh on focus |

Do not write grievances directly to Postgres from the browser.

## UX patterns (modules A–H)

1. **Reference ID** — prominent after submit; copy button; use on track page.
2. **Three-layer labeling**
   - General guidance (chatbot help text)
   - “Suggested by AI” (category, dept, priority, image hints)
   - “Official” (officer-set fields, status, remarks on citizen track = public messages only)
3. **Lifecycle** — show citizen-friendly labels mapped from status (see API contract).
4. **Needs information** — dedicated UI when status is `needs_information`.
5. **SLA** — show due dates and warnings; never promise exact resolution dates from AI.
6. **Feedback** — form only when status `resolved`/`closed`; one submission.
7. **Notifications** — inbox + preferences screen (MVP in-app only).
8. **Attachments** — Phase Next; show placeholder or hide until API exists.
9. **Chatbot** — Phase Next; confirm before final grievance submit.
10. **Community / WhatsApp / voice** — hide or “coming soon” unless backend feature flag enabled.

## Suggested routes

| Path | Audience |
|------|----------|
| `/`, `/login`, `/register` | Public |
| `/dashboard` | Citizen — my grievances |
| `/grievances/new` | Citizen — submit + follow-ups |
| `/track/:referenceId` | Citizen — optional public track by ref + auth |
| `/grievances/:id` | Citizen / officer |
| `/officer/queue` | Officer |
| `/dept/queue` | Department admin (Next) |
| `/admin/departments`, `/admin/categories`, `/admin/sla` | Platform admin |
| `/admin/analytics` | Admin dashboards |
| `/notifications`, `/settings/notifications` | All authenticated |
| `/community/*` | Future — do not ship until API marked implemented |

## API client

- Central `apiClient` with auth header injection and error envelope parsing.
- Phase 4: optional OpenAPI-generated types from backend.

## Accessibility and i18n

- Plan for Telugu + English copy hooks (`locale` from `/me`).
- MVP may ship English UI with backend locale field ready.

## Disclaimer in UI footer

Platform is under development; not an official government portal unless configured and authorized by deployer.

## CORS

Dev: `http://localhost:5173`. Production: Vercel URL in backend `CORS_ORIGINS`.
