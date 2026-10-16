# RTGS — Real-Time Governance Society

Citizen-centric digital urban governance: AI-assisted grievance redressal, SLA-aware operations, and staged multichannel intake (web first).

**Phase 4 status:** Deployment readiness (Render blueprint, CI, smoke docs, shared `frontend/src/lib` API client). **Claude UI not in repo** — integration blocked until Vite app is imported. Live Supabase smoke **not verified** (no `backend/.env` in workspace).

RTGS is **not** presented as an official government service unless your deployer explicitly configures and authorizes that relationship.

## Directory structure

```
.
├── frontend/                 # Claude UI (React + Vite)
├── backend/                  # FastAPI application
├── supabase/
│   ├── migrations/           # Apply in filename order
│   └── seed.sql
├── docs/
└── PROJECT_SPEC.md, ARCHITECTURE.md, DEVELOPMENT_PLAN.md
```

## Migrations (Supabase dev)

Apply in order:

1. `20251016120000_initial_schema.sql`
2. `20251016130000_platform_redesign_extensions.sql`
3. `20251016140000_rls_role_helpers.sql`
4. `20251016150000_phase3_ai_provenance.sql`

Using Supabase CLI (recommended):

```bash
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
psql "$DATABASE_URL" -f supabase/seed.sql
```

Or run each SQL file in the Supabase SQL editor on a **dev** project only.

**Live Supabase:** not verified in CI; configure `backend/.env` with your dev project credentials to test end-to-end.

## Backend setup (Python 3.9+; 3.11+ recommended)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: DATABASE_URL (Supabase pooler), SUPABASE_JWT_SECRET, etc.
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs  
- OpenAPI JSON: http://localhost:8000/openapi.json  
- Health: http://localhost:8000/api/v1/health  

### Local dev without Supabase JWT

For local testing only (never production):

```env
AUTH_DEV_BYPASS=true
AUTH_DEV_USER_ID=<uuid from profiles table>
DATABASE_URL=sqlite+aiosqlite:///./rtgs_dev.db
```

Create tables with migrations against Postgres, or use pytest (in-memory SQLite fixtures).

### Account provisioning

See [backend/docs/ACCOUNT_PROVISIONING.md](backend/docs/ACCOUNT_PROVISIONING.md).

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

**Last run:** 25 passed (unit + mocked integration on SQLite; no live Supabase in CI).

### Live Supabase verification (manual)

When `backend/.env` is configured:

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --port 8000
curl -s http://localhost:8000/api/v1/health | jq .
```

Apply migrations via `supabase db push`, create private bucket per `supabase/storage/complaint-attachments-policy.md`, provision roles per `backend/docs/ACCOUNT_PROVISIONING.md`.

## Frontend setup (Phase 4)

Copy `frontend/.env.example` → `frontend/.env.local` and set `VITE_API_BASE_URL=http://localhost:8000`.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/API_CONTRACT.md](docs/API_CONTRACT.md) | REST contract + implementation status |
| [docs/FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md) | Claude UI integration |
| [backend/docs/ACCOUNT_PROVISIONING.md](backend/docs/ACCOUNT_PROVISIONING.md) | Roles and officers |

## Workflow

- **Claude:** frontend UI/UX in `frontend/`
- **Cursor:** backend, database, AI, tests, deployment

## Git history

`9903103` → Phase 1 foundation · `1ef5695` → Phase 1 redesign · Phase 2 backend commits follow on `main`.

## License

TBD by project owners.
