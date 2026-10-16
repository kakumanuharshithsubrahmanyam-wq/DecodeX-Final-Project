# RTGS staging deploy (Render + Vercel + rtgs-dev)

**Production:** do not use these steps for production.

## 0. Secrets (local only)

1. Copy `.env.rtgs.example` → `.env.rtgs` at repo root (gitignored).
2. Fill values from [Supabase Dashboard → rtgs-dev](https://supabase.com/dashboard/project/fsnqpcomhtseoffwgfub/settings/api) (Database password, `service_role`, anon/publishable key).
3. Run:

```bash
bash backend/scripts/bootstrap_from_env_rtgs.sh
python backend/scripts/check_dev_env.py
```

## 1. Git remote (required for Render auto-deploy)

This repo has **no `git remote`** yet. Render web services deploy from Git. Either:

- Add a GitHub/GitLab remote and push `main` (when you approve push), then connect that repo in Render, **or**
- Create the service in the [Render Dashboard](https://dashboard.render.com/) and paste env vars manually.

Do **not** overwrite unrelated services (e.g. `resumefit-ai-api`).

## 2. Render — `rtgs-api`

Workspace: **My Workspace** (`tea-db89jcgu01pc73f1ajn0`) — CLI authenticated.

Suggested service:

| Setting | Value |
|---------|--------|
| Name | `rtgs-api` |
| Root directory | `backend` |
| Runtime | Python 3.11 |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health | `/api/v1/health` |

Dashboard env (from `backend/.env` after bootstrap — never commit):

- `APP_ENV=staging`
- `AUTH_DEV_BYPASS=false`
- `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_ISSUER=https://fsnqpcomhtseoffwgfub.supabase.co/auth/v1`
- `JWT_AUDIENCE=authenticated`
- `CORS_ORIGINS=https://<your-vercel-preview-host>` (exact origin, no `*` with credentials)
- Optional: `SUPABASE_JWT_SECRET` only if not using JWKS

Verify:

```bash
curl -sS "https://<rtgs-api-host>/api/v1/health"
# expect "database": "ok"
```

## 3. Vercel — frontend staging (team `harshith-debug`)

```bash
cd frontend
vercel link   # new project e.g. rtgs-portal
vercel env add VITE_API_BASE_URL preview
vercel env add VITE_SUPABASE_URL preview
vercel env add VITE_SUPABASE_ANON_KEY preview
vercel deploy   # preview URL — not --prod
```

Public vars only. Never set service role on Vercel.

## 4. Supabase Auth redirects

In [Auth URL configuration](https://supabase.com/dashboard/project/fsnqpcomhtseoffwgfub/auth/url-configuration):

- **Site URL:** Vercel staging origin
- **Redirect URLs:** same origin + `/` paths used by login/password recovery

Update Render `CORS_ORIGINS` to match the Vercel staging origin exactly.

## 5. Live tests

```bash
cd backend && RTGS_LIVE_TEST=1 pytest tests/test_live_workflow.py -q
cd frontend && PLAYWRIGHT_BASE_URL=https://<vercel-preview> E2E_LIVE=1 npm run test:e2e
```
