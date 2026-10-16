# Importing `rtgs-frontend.zip`

## Prerequisite

Place **`rtgs-frontend.zip`** at the repository root (same folder as `README.md`):

```text
DecodeX Final Project/rtgs-frontend.zip
```

If the archive is missing, integration **must not** proceed with a fabricated UI.

## Safe import (preserve `src/lib/`)

1. Unzip to a temporary directory and confirm `src/App.tsx`, `vite.config.ts`, and `package.json` exist.
2. Copy the supplied app into `frontend/`, **merging** with existing files:
   - Keep `frontend/src/lib/api-client.ts`, `auth.ts`, `types.ts` (wire screens to these).
   - Keep `frontend/.env.example` and extend if the zip includes its own env template.
3. Resolve `package.json` dependencies (React Router, Lucide, Recharts, `@supabase/supabase-js`).
4. Configure path alias `@/` → `src/` if not already in `vite.config.ts`.
5. Remove or gate demo `localStorage` grievance data; keep language/theme preferences only.
6. Run `npm install`, `npm run build`, and backend `pytest`.

## After import (Cursor task checklist)

- Accessibility pass on `styles.css` (18px body, 44px targets, focus rings).
- Full `src/i18n/` for English and Telugu.
- Supabase Auth screens; role from `GET /api/v1/me` only.
- Connect workflows per [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md).
