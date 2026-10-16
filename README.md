# RTGS — Real-Time Governance Society

Citizen-centric digital urban governance: AI-assisted grievance redressal, SLA-aware operations, and staged multichannel intake (web first).

**Phase 1 (redesign) status:** Architecture, data model, API contract, and SQL migrations documented. **No runnable app yet.** Phase 2 implements FastAPI and applies migrations to a dev Supabase project.

RTGS is **not** presented as an official government service unless your deployer explicitly configures and authorizes that relationship.

## Directory structure

```
.
├── frontend/                 # Claude UI (React + Vite)
├── backend/                  # FastAPI + AI (Phase 2+)
├── supabase/
│   ├── migrations/           # Apply in filename order
│   └── seed.sql
├── docs/
│   ├── API_CONTRACT.md
│   ├── FRONTEND_INTEGRATION.md
│   ├── FEATURE_MATRIX.md
│   ├── DATA_MODEL.md
│   └── INTEGRATIONS.md
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
└── DEVELOPMENT_PLAN.md
```

## Migrations

1. `20251016120000_initial_schema.sql`
2. `20251016130000_platform_redesign_extensions.sql`

Do not edit applied migrations; add new files for schema changes.

## Documentation index

| Document | Purpose |
|----------|---------|
| [PROJECT_SPEC.md](./PROJECT_SPEC.md) | Vision, modules A–H, MVP vs staged |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Components, AI pipeline, security |
| [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) | Four-phase plan |
| [docs/FEATURE_MATRIX.md](./docs/FEATURE_MATRIX.md) | Features, roles, acceptance criteria |
| [docs/DATA_MODEL.md](./docs/DATA_MODEL.md) | Entities, lifecycle, RLS plan |
| [docs/API_CONTRACT.md](./docs/API_CONTRACT.md) | REST contract (MVP/Next/Future tags) |
| [docs/INTEGRATIONS.md](./docs/INTEGRATIONS.md) | WhatsApp, notifications, AI providers |

## Setup (Phase 2+)

1. Copy `frontend/.env.example` → `frontend/.env.local`
2. Copy `backend/.env.example` → `backend/.env`
3. Apply Supabase migrations; run `seed.sql` on dev only
4. Start backend and frontend (instructions added in Phase 2)

## Workflow

- **Claude:** frontend UI/UX in `frontend/`
- **Cursor:** backend, database, AI, tests, deployment

## Git history

Initial foundation commit `9903103` preserved; redesign commits follow on `main`.

## License

TBD by project owners.
