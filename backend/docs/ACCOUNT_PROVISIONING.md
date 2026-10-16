# RTGS account provisioning (secure)

Roles **must not** be assigned via Supabase `user_metadata` or client-editable JWT claims.

## Citizens

1. User registers through Supabase Auth (frontend).
2. Trigger `handle_new_user` creates `profiles` row with `role = citizen`.

## Officers and administrators

Use a trusted server path only:

1. Create the user in Supabase Auth (dashboard or Admin API with **service role** on backend).
2. Update `profiles.role` via SQL or a platform-admin-only API using the service role:

```sql
update public.profiles
set role = 'officer'
where email = 'officer@example.com';

insert into public.department_officers (department_id, officer_id)
select d.id, p.id
from public.departments d, public.profiles p
where d.code = 'SAN' and p.email = 'officer@example.com';
```

Supported roles: `officer`, `department_administrator`, `platform_administrator`, `community_moderator`.

Legacy `administrator` is treated as `platform_administrator` in the API.

## Community moderators

Assign `community_moderator` only. This role must **not** grant access to private grievance rows (enforced in FastAPI and future RLS hardening).

## Local development / tests

Set in `backend/.env` (never in production):

```
AUTH_DEV_BYPASS=true
AUTH_DEV_USER_ID=<uuid matching profiles.id>
AUTH_DEV_ROLE=citizen
```

JWT verification uses `SUPABASE_JWT_SECRET` with HS256 when bypass is disabled.
