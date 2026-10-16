# RTGS End-to-End Smoke Test (development only)

Run only against a **dedicated dev** Supabase project and dev/staging API. Do not use production citizen data.

## Automated (API + dev bypass — not live Supabase Auth)

```bash
cd backend && source .venv/bin/activate && pytest -q
```

This validates grievance flows with SQLite mocks (25+ tests). **This is not a live Supabase smoke test.**

## Optional live script

Requires `backend/.env` with real `DATABASE_URL` and `AUTH_DEV_BYPASS=true` plus seeded profiles:

```bash
cd backend && source .venv/bin/activate
python scripts/smoke_dev_bypass.py
```

Exit code 0 only if health + create grievance succeed against configured Postgres.

## Manual E2E (real Supabase Auth) — checklist

1. **Citizen sign-in** via Supabase Auth in the frontend (`/login`).
2. **Submit grievance** with vague text → receive reference ID; verify `needs_information` or follow-up questions from `POST .../analyze`.
3. **Submit additional info** → status moves toward review.
4. **Attachment** (optional): upload-url → PUT to signed URL → complete → download-url as same user.
5. **Officer sign-in** (role provisioned in DB) → list dept/assigned queue → assign → transition `in_progress` → `resolved` → `closed`.
6. **Citizen feedback** on closed/resolved grievance.
7. **Notifications** list shows submission/status events.
8. **Negative tests:**
   - Citizen B cannot `GET` citizen A's grievance (403/404).
   - Expired/invalid JWT → 401.
   - Community moderator (if provisioned) cannot access private grievance APIs.

Record results in your run log; do not claim live verification unless each step was executed against dev.

## Attachment verification

| Step | Expected |
|------|----------|
| Oversized file | 400 VALIDATION_ERROR |
| Wrong MIME type | 400 |
| Upload without auth | 401 |
| Download other citizen's file | 403/404 |
| Success | `upload_status: completed` only after `complete` endpoint |

Mock Storage URLs in local dev without `SUPABASE_SERVICE_ROLE_KEY` do **not** prove real Storage uploads.
