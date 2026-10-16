# Phase 6 design reference archive

## Expected archive (not in workspace)

Phase 6 specifies a vanilla HTML/CSS/JS reference extracted as:

- **Expected path:** `rtgs-frontend-new.zip` (from uploaded `rtgs-frontend(1).zip`)
- **Expected contents:** `rtgs/index.html`, `rtgs/styles.css`, `rtgs/app.js`, `rtgs/README.md`

**Status:** As of this phase, neither `rtgs-frontend-new.zip` nor `rtgs-frontend(1).zip` was present under the repository workspace. Archive-dependent pixel matching was **not** performed.

## What was done instead

The existing React app (`frontend/src/RtgsPortal.tsx`, `frontend/src/styles.css`) already implements a **blue/white civic identity** (navy hero, `#4168cf` accents, card-based dashboards, complaint wizard, officer/admin surfaces). Phase 6:

- Reordered citizen navigation to foreground **File a complaint**, **Track a complaint**, and **Get help**.
- Continued EN/TE localization for remaining portal screens.
- Preserved FastAPI + Supabase integration, role mapping, and demo/live separation.

## When the archive is added

1. Place `rtgs-frontend-new.zip` at the repository root or `frontend/`.
2. Extract to a read-only reference folder (e.g. `design/reference/rtgs/`) — do **not** replace the Vite app.
3. Diff typography, spacing, and component patterns against `frontend/src/styles.css` and port deltas into React components.

## Demo-only reference behaviors (never ship as production)

- Role selector in the browser
- `localStorage` grievance database
- Keyword-only “AI” and simulated image analysis
- Local-only SLA saves presented as server policy
- Sample analytics months without API backing
