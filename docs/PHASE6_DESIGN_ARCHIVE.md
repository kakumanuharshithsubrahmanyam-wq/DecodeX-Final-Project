# Phase 6 design reference archive

## Design reference archive

- **Workspace paths:** `rtgs-frontend-new.zip` (repo root) and `frontend/rtgs-frontend-new.zip`
- **Extracted reference:** `design/reference/rtgs/` (`index.html`, `styles.css`, `app.js`, `README.md`)

**Inspected:** October 2026 — vanilla JS demo with LocalStorage (`rtgs1`), role picker login, keyword AI, EN/TE string table. **Not imported into React** (by design).

## Visual patterns ported into React (Phase 6B)

| Reference element | React implementation |
|-------------------|----------------------|
| Light blue page background (`#eef4fd`) | `frontend/src/styles.css` tokens `--bg`, hero gradient |
| Primary civic blue buttons (`#1d5fd6` / `#1d63e8`) | `.btn-primary`, brand mark, nav primary items |
| Landing pill + two-line hero headline | `portal.landing.pill`, `heroTitle1/2`, `Landing` in `RtgsPortal.tsx` |
| Prominent File / Track / Help actions | Citizen nav order + hero CTAs |
| Table header tint, pills, status badges | Existing table/badge components + CSS alignment |
| Complaint wizard steps, review cards, officer queue layout | Retained React structure; copy wired to `portal.*` i18n |

**Not ported (intentionally):** localStorage grievance DB, demo role selector login, reference `app.js` routing, simulated persistence, keyword-only AI as production behavior.

## Maintenance

1. Keep the ZIP as a read-only reference; extract to `design/reference/rtgs/` when updating.
2. Diff typography and spacing against `frontend/src/styles.css` and port deltas into React — never replace the Vite app with vanilla JS.

## Demo-only reference behaviors (never ship as production)

- Role selector in the browser
- `localStorage` grievance database
- Keyword-only “AI” and simulated image analysis
- Local-only SLA saves presented as server policy
- Sample analytics months without API backing
