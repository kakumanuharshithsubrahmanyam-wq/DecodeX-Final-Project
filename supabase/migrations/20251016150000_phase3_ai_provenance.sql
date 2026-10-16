-- Phase 3: AI provenance and attachment upload status

alter table public.ai_analyses
  add column if not exists detected_language text,
  add column if not exists provider_name text,
  add column if not exists provider_model text;

alter table public.attachments
  add column if not exists upload_status text not null default 'pending'
    check (upload_status in ('pending', 'completed', 'failed'));

comment on column public.ai_analyses.detected_language is 'ISO-ish language code: en, te, mixed';
comment on column public.attachments.upload_status is 'pending until client completes signed upload';
