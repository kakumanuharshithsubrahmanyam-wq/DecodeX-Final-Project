# Apply RTGS migrations (forward-only)

Use only on the dedicated **rtgs-dev** Supabase project (or a new empty dev project).

1. Install [Supabase CLI](https://supabase.com/docs/guides/cli).
2. `supabase login`
3. `supabase link --project-ref <RTGS_DEV_REF>`
4. `supabase migration list` — compare with repository files under `supabase/migrations/`.
5. `supabase db push` — applies pending migrations in filename order.
6. Optional dev seed: `psql "$DATABASE_URL" -f supabase/seed.sql` (departments/categories/SLA only; no fake citizens).
7. Storage: `psql "$DATABASE_URL" -f supabase/scripts/create_storage_bucket.sql`
8. Auth: configure Site URL and redirect URLs for Vercel + localhost in Supabase dashboard.

**Do not** run against TEAM-DDMM, printkiosk, or other unrelated projects.

If project creation fails with a free-tier limit, pause or upgrade an existing project in the Supabase dashboard, then create `rtgs-dev`.
