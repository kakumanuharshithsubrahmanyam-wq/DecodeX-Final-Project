# Frontend integration guide (Claude UI)

This document summarizes how the Claude-built React app should integrate with RTGS backend and Supabase.

## Stack

- React 18+, TypeScript, Vite, Tailwind CSS, shadcn/ui where it fits existing patterns.
- Place all app source under `frontend/` (standard Vite layout: `src/`, `index.html`, etc.).

## Environment

From `frontend/.env.example`:

- `VITE_API_BASE_URL` — FastAPI origin.
- `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` — Auth only (publishable key).

Never embed the Supabase service role key in the frontend.

## Authentication

1. Use `@supabase/supabase-js` for sign-up, sign-in, sign-out, and session refresh.
2. Read `session.access_token` and attach to every API call:

```typescript
headers: {
  Authorization: `Bearer ${accessToken}`,
  'Content-Type': 'application/json',
}
```

3. Route guards by `GET /api/v1/me` → `data.role` (`citizen` | `officer` | `administrator`).

## Data fetching

- **Grievances, AI, assignments, analytics:** FastAPI only (`docs/API_CONTRACT.md`).
- Do not write grievances directly to Supabase tables from the browser (audit + AI orchestration live on the API).

## UX requirements

- Show **reference_id** prominently after submit (copy button).
- Label AI fields: “Suggested by AI” vs official category/department/priority (officer-editable).
- Handle API error envelope (`error.code`, `error.message`, `error.details`).
- List screens: loading skeleton, empty state, retry on 5xx.
- Dates: format ISO timestamps for locale in UI; store/transmit ISO 8601 unchanged.

## Suggested routes

| Path | Audience | Notes |
|------|----------|--------|
| `/login`, `/register` | Public | Supabase Auth |
| `/dashboard` | Citizen | My grievances |
| `/grievances/new` | Citizen | Create + follow-up flow |
| `/grievances/:id` | Citizen / officer | Detail + timeline |
| `/officer/queue` | Officer | Assigned / department cases |
| `/admin/departments` | Admin | Department CRUD |
| `/admin/analytics` | Admin | Overview metrics |

## Attachments (Phase 4)

1. Request signed URL from API.
2. PUT file to signed URL.
3. Confirm completion endpoint when implemented.

## CORS

Backend will allow local Vite origins in development (`http://localhost:5173`). Production: Vercel domain added on Render env `CORS_ORIGINS`.
