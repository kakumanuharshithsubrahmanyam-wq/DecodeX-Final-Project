-- RTGS platform redesign extensions (Phase 1 blueprint — apply after initial_schema)
-- Preserves 20251016120000_initial_schema.sql history; do not edit prior migration.

-- ---------------------------------------------------------------------------
-- Roles (extend enum; keep legacy 'administrator' for backward compatibility)
-- ---------------------------------------------------------------------------
alter type public.user_role add value if not exists 'department_administrator';
alter type public.user_role add value if not exists 'platform_administrator';
alter type public.user_role add value if not exists 'community_moderator';

-- ---------------------------------------------------------------------------
-- Grievance lifecycle (extend enum)
-- Canonical flow: submitted → needs_information | under_review → assigned →
-- in_progress → resolved → closed; reopened and escalated as documented.
-- Legacy value in_review remains valid; application maps to under_review in UI.
-- ---------------------------------------------------------------------------
alter type public.grievance_status add value if not exists 'needs_information';
alter type public.grievance_status add value if not exists 'under_review';
alter type public.grievance_status add value if not exists 'reopened';

create type public.intake_channel as enum (
  'web',
  'mobile_web',
  'whatsapp',
  'voice',
  'chatbot',
  'api'
);

-- ---------------------------------------------------------------------------
-- Category taxonomy (MVP)
-- ---------------------------------------------------------------------------
create table public.grievance_categories (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references public.grievance_categories (id) on delete set null,
  code text not null unique,
  name text not null,
  description text,
  default_department_id uuid references public.departments (id) on delete set null,
  is_active boolean not null default true,
  sort_order integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index grievance_categories_parent_idx on public.grievance_categories (parent_id);
create index grievance_categories_active_idx on public.grievance_categories (is_active)
  where is_active = true;

create trigger grievance_categories_updated_at
  before update on public.grievance_categories
  for each row execute function public.set_updated_at();

-- Link grievances to official category taxonomy
alter table public.grievances
  add column if not exists category_id uuid references public.grievance_categories (id) on delete set null,
  add column if not exists subcategory_id uuid references public.grievance_categories (id) on delete set null,
  add column if not exists intake_channel public.intake_channel not null default 'web',
  add column if not exists intake_external_id text,
  add column if not exists ward_or_locality text,
  add column if not exists reopened_count integer not null default 0;

create index grievances_category_idx on public.grievances (category_id);

-- ---------------------------------------------------------------------------
-- SLA policies and per-grievance deadlines (MVP)
-- ---------------------------------------------------------------------------
create table public.sla_policies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  priority public.priority_level not null,
  category_id uuid references public.grievance_categories (id) on delete set null,
  department_id uuid references public.departments (id) on delete set null,
  first_response_hours integer not null check (first_response_hours > 0),
  resolution_hours integer not null check (resolution_hours > 0),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index sla_policies_lookup_idx on public.sla_policies (priority, category_id, department_id)
  where is_active = true;

create trigger sla_policies_updated_at
  before update on public.sla_policies
  for each row execute function public.set_updated_at();

create table public.grievance_sla (
  grievance_id uuid primary key references public.grievances (id) on delete cascade,
  policy_id uuid references public.sla_policies (id) on delete set null,
  first_response_due_at timestamptz,
  resolution_due_at timestamptz,
  first_response_at timestamptz,
  breached_first_response boolean not null default false,
  breached_resolution boolean not null default false,
  updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Duplicate / related grievances (next-phase table; schema ready)
-- ---------------------------------------------------------------------------
create table public.grievance_relations (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  related_grievance_id uuid not null references public.grievances (id) on delete cascade,
  relation_type text not null check (relation_type in ('duplicate_candidate', 'related', 'merged_into')),
  confidence numeric(5, 4),
  created_by uuid references public.profiles (id) on delete set null,
  created_at timestamptz not null default now(),
  unique (grievance_id, related_grievance_id, relation_type),
  check (grievance_id <> related_grievance_id)
);

create index grievance_relations_grievance_idx on public.grievance_relations (grievance_id);

-- ---------------------------------------------------------------------------
-- Citizen feedback (MVP)
-- ---------------------------------------------------------------------------
create table public.citizen_feedback (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  citizen_id uuid not null references public.profiles (id) on delete restrict,
  rating smallint not null check (rating between 1 and 5),
  satisfaction_score smallint check (satisfaction_score between 1 and 5),
  comment text,
  improvement_suggestion text,
  is_public boolean not null default false,
  created_at timestamptz not null default now(),
  unique (grievance_id, citizen_id)
);

create index citizen_feedback_grievance_idx on public.citizen_feedback (grievance_id);

-- ---------------------------------------------------------------------------
-- Notification preferences (MVP) and delivery attempts (next-phase observability)
-- ---------------------------------------------------------------------------
create table public.notification_preferences (
  user_id uuid primary key references public.profiles (id) on delete cascade,
  in_app_enabled boolean not null default true,
  email_enabled boolean not null default false,
  sms_enabled boolean not null default false,
  web_push_enabled boolean not null default false,
  whatsapp_enabled boolean not null default false,
  marketing_campaigns_enabled boolean not null default false,
  emergency_alerts_enabled boolean not null default true,
  quiet_hours_start time,
  quiet_hours_end time,
  locale text not null default 'en',
  updated_at timestamptz not null default now()
);

create trigger notification_preferences_updated_at
  before update on public.notification_preferences
  for each row execute function public.set_updated_at();

create type public.notification_channel as enum (
  'in_app',
  'email',
  'sms',
  'web_push',
  'whatsapp'
);

create type public.delivery_status as enum (
  'pending',
  'sent',
  'delivered',
  'failed',
  'skipped'
);

create table public.notification_delivery_attempts (
  id uuid primary key default gen_random_uuid(),
  notification_id uuid not null references public.notifications (id) on delete cascade,
  channel public.notification_channel not null,
  provider text,
  provider_message_id text,
  status public.delivery_status not null default 'pending',
  error_code text,
  attempted_at timestamptz not null default now(),
  completed_at timestamptz
);

create index notification_delivery_notification_idx
  on public.notification_delivery_attempts (notification_id);

-- Extend notifications for channel abstraction
alter table public.notifications
  add column if not exists channel public.notification_channel not null default 'in_app',
  add column if not exists dedupe_key text;

create unique index notifications_dedupe_idx on public.notifications (user_id, dedupe_key)
  where dedupe_key is not null;

-- ---------------------------------------------------------------------------
-- Image analysis metadata (advisory; next-phase processing)
-- ---------------------------------------------------------------------------
alter table public.attachments
  add column if not exists attachment_role text not null default 'evidence'
    check (attachment_role in ('evidence', 'before', 'after', 'resolution')),
  add column if not exists image_analysis jsonb,
  add column if not exists exif_location_confirmed boolean,
  add column if not exists quality_flags jsonb not null default '[]'::jsonb;

-- ---------------------------------------------------------------------------
-- Integration event log (multichannel intake — next phase)
-- ---------------------------------------------------------------------------
create table public.integration_events (
  id uuid primary key default gen_random_uuid(),
  channel public.intake_channel not null,
  direction text not null check (direction in ('inbound', 'outbound')),
  external_id text,
  payload_summary jsonb not null default '{}'::jsonb,
  grievance_id uuid references public.grievances (id) on delete set null,
  status text not null default 'received',
  created_at timestamptz not null default now()
);

create index integration_events_channel_created_idx
  on public.integration_events (channel, created_at desc);

-- ---------------------------------------------------------------------------
-- RLS for new tables
-- ---------------------------------------------------------------------------
alter table public.grievance_categories enable row level security;
alter table public.sla_policies enable row level security;
alter table public.grievance_sla enable row level security;
alter table public.grievance_relations enable row level security;
alter table public.citizen_feedback enable row level security;
alter table public.notification_preferences enable row level security;
alter table public.notification_delivery_attempts enable row level security;
alter table public.integration_events enable row level security;

create policy "Authenticated read active categories"
  on public.grievance_categories for select
  to authenticated
  using (is_active = true or public.is_administrator());

create policy "Platform admin manage categories"
  on public.grievance_categories for all
  using (public.is_administrator())
  with check (public.is_administrator());

create policy "Citizen read own feedback"
  on public.citizen_feedback for select
  using (citizen_id = auth.uid() or public.is_administrator());

create policy "Citizen insert own feedback"
  on public.citizen_feedback for insert
  with check (citizen_id = auth.uid());

create policy "User manage own notification preferences"
  on public.notification_preferences for all
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy "User read own delivery attempts"
  on public.notification_delivery_attempts for select
  using (
    exists (
      select 1 from public.notifications n
      where n.id = notification_delivery_attempts.notification_id
        and n.user_id = auth.uid()
    )
    or public.is_administrator()
  );

comment on table public.grievance_categories is 'Official taxonomy; AI suggestions reference category codes separately in ai_analyses.';
comment on table public.citizen_feedback is 'One feedback per citizen per grievance; not used for automatic worker penalties.';
