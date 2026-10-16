# RTGS — Real-Time Governance Society

AI-assisted government grievance intake, routing, prioritization, and resolution tracking.

**Phase 1 status:** Repository foundation, documentation, API contract, and draft database schema. Application code begins in Phase 2.

## Directory structure

```
.
├── frontend/                 # React + Vite (Claude UI lands here)
│   └── .env.example
├── backend/                  # FastAPI + AI pipeline (Phase 2+)
│   └── .env.example
├── supabase/
│   ├── migrations/           # PostgreSQL schema
│   └── seed.sql              # Sample departments (dev)
├── docs/
│   └── API_CONTRACT.md       # Integration contract for frontend
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT_PLAN.md
└── README.md
```

## Prerequisites (upcoming phases)

- Node.js 20+ (frontend)
- Python 3.11+ (backend)
- Supabase project (Postgres + Auth)
- Optional: Supabase CLI for local migration workflow

## Setup (Phase 2+)

1. Copy environment templates:
   - `frontend/.env.example` → `frontend/.env.local`
   - `backend/.env.example` → `backend/.env`
2. Fill placeholders from your Supabase dashboard (never commit real secrets).
3. Apply migrations from `supabase/migrations/` to your dev project.
4. Run backend and frontend per instructions added in Phase 2.

## Documentation

| Document | Purpose |
|----------|---------|
| [PROJECT_SPEC.md](./PROJECT_SPEC.md) | Product scope, roles, MVP vs deferred |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, auth, deployment |
| [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) | Four-phase delivery plan |
| [docs/API_CONTRACT.md](./docs/API_CONTRACT.md) | REST API for Claude/Cursor integration |

## Workflow

- **Claude:** UI/UX in `frontend/`
- **Cursor:** backend, database, AI, tests, deployment

## License

TBD by project owners.
