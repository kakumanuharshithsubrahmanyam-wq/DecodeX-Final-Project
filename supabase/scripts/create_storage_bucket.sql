-- Run once on RTGS dev Supabase (SQL editor or psql). Bucket must stay private.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'complaint-attachments',
  'complaint-attachments',
  false,
  5242880,
  array['image/jpeg', 'image/png', 'image/webp', 'application/pdf']::text[]
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- Deny public anon access; uploads/downloads go through backend-signed URLs only.
-- Add object policies in dashboard if using direct client storage (RTGS uses API signing).
