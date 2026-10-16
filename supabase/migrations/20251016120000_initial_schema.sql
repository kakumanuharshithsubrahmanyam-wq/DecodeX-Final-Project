-- RTGS initial schema (draft — apply in Phase 2 to dev Supabase only)
-- Requires Supabase Auth; profiles.id references auth.users

-- Extensions
create extension if not exists "pgcrypto";

-- Enums
create type public.user_role as enum ('citizen', 'officer', 'administrator');

create type public.grievance_status as enum (
  'submitted',
  'in_review',
  'assigned',
  'in_progress',
  'resolved',
  'closed',
  'escalated'
);

create type public.priority_level as enum ('low', 'medium', 'high', 'critical');

create type public.ai_source as enum ('rules', 'llm');

create type public.grievance_event_type as enum (
  'status_change',
  'remark',
  'assignment',
  'analysis',
  'attachment',
  'feedback'
);

-- Profiles (1:1 with auth.users)
create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null,
  full_name text,
  phone text,
  role public.user_role not null default 'citizen',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index profiles_role_idx on public.profiles (role);
create index profiles_email_idx on public.profiles (email);

-- Departments
create table public.departments (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  code text not null unique,
  description text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Officer ↔ department (admins manage)
create table public.department_officers (
  department_id uuid not null references public.departments (id) on delete cascade,
  officer_id uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (department_id, officer_id),
  constraint department_officers_officer_is_officer
    check (true) -- enforced in app: profile.role = officer
);

create index department_officers_officer_idx on public.department_officers (officer_id);

-- Grievances
create table public.grievances (
  id uuid primary key default gen_random_uuid(),
  reference_id text not null unique,
  citizen_id uuid not null references public.profiles (id) on delete restrict,
  title text,
  description text not null,
  location_text text not null,
  latitude double precision,
  longitude double precision,
  status public.grievance_status not null default 'submitted',
  -- Official fields (human decisions)
  official_category text,
  official_department_id uuid references public.departments (id) on delete set null,
  official_priority public.priority_level,
  -- Cached from latest analysis for list views (optional denormalization)
  urgency_score numeric(5, 4),
  requires_human_review boolean not null default false,
  resolution_due_at timestamptz,
  resolved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint grievances_description_min_length check (char_length(description) >= 20)
);

create index grievances_citizen_id_idx on public.grievances (citizen_id);
create index grievances_status_idx on public.grievances (status);
create index grievances_official_department_idx on public.grievances (official_department_id);
create index grievances_created_at_idx on public.grievances (created_at desc);
create index grievances_reference_id_idx on public.grievances (reference_id);

-- Assignments (history of responsibility)
create table public.assignments (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  department_id uuid not null references public.departments (id) on delete restrict,
  officer_id uuid references public.profiles (id) on delete set null,
  assigned_by uuid references public.profiles (id) on delete set null,
  assigned_at timestamptz not null default now(),
  unassigned_at timestamptz,
  is_current boolean not null default true
);

create index assignments_grievance_current_idx on public.assignments (grievance_id)
  where is_current = true;
create index assignments_officer_idx on public.assignments (officer_id)
  where is_current = true;

-- Timeline
create table public.grievance_events (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  event_type public.grievance_event_type not null,
  from_status public.grievance_status,
  to_status public.grievance_status,
  remark text,
  metadata jsonb not null default '{}'::jsonb,
  actor_id uuid references public.profiles (id) on delete set null,
  created_at timestamptz not null default now()
);

create index grievance_events_grievance_created_idx
  on public.grievance_events (grievance_id, created_at);

-- AI analyses (versioned)
create table public.ai_analyses (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  version integer not null,
  source public.ai_source not null default 'rules',
  summary text not null,
  extracted_entities jsonb not null default '{}'::jsonb,
  suggested_category text,
  suggested_department_id uuid references public.departments (id) on delete set null,
  urgency_score numeric(5, 4) not null default 0,
  urgency_label public.priority_level not null default 'low',
  confidence numeric(5, 4) not null default 0,
  requires_human_review boolean not null default true,
  explanation text,
  follow_up_questions jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  unique (grievance_id, version)
);

create index ai_analyses_grievance_created_idx
  on public.ai_analyses (grievance_id, created_at desc);

-- Attachments (binary in Storage)
create table public.attachments (
  id uuid primary key default gen_random_uuid(),
  grievance_id uuid not null references public.grievances (id) on delete cascade,
  uploaded_by uuid not null references public.profiles (id) on delete restrict,
  file_name text not null,
  content_type text not null,
  size_bytes bigint not null,
  storage_path text not null,
  created_at timestamptz not null default now()
);

create index attachments_grievance_idx on public.attachments (grievance_id);

-- Notifications
create table public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  type text not null,
  title text not null,
  body text not null,
  grievance_id uuid references public.grievances (id) on delete set null,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create index notifications_user_unread_idx on public.notifications (user_id, created_at desc)
  where read_at is null;

-- Audit logs (admin / security)
create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references public.profiles (id) on delete set null,
  action text not null,
  resource_type text not null,
  resource_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  ip_address inet,
  created_at timestamptz not null default now()
);

create index audit_logs_created_idx on public.audit_logs (created_at desc);
create index audit_logs_resource_idx on public.audit_logs (resource_type, resource_id);

-- updated_at trigger helper
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

create trigger departments_updated_at
  before update on public.departments
  for each row execute function public.set_updated_at();

create trigger grievances_updated_at
  before update on public.grievances
  for each row execute function public.set_updated_at();

-- Auto-create profile on signup (role defaults to citizen; admins promoted via service role)
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name')
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- RLS
alter table public.profiles enable row level security;
alter table public.departments enable row level security;
alter table public.department_officers enable row level security;
alter table public.grievances enable row level security;
alter table public.assignments enable row level security;
alter table public.grievance_events enable row level security;
alter table public.ai_analyses enable row level security;
alter table public.attachments enable row level security;
alter table public.notifications enable row level security;
alter table public.audit_logs enable row level security;

-- Helper: current user role from profiles (not JWT user_metadata)
create or replace function public.current_user_role()
returns public.user_role
language sql
stable
security definer
set search_path = public
as $$
  select role from public.profiles where id = auth.uid();
$$;

create or replace function public.is_administrator()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'administrator' and is_active = true
  );
$$;

create or replace function public.is_officer_of_department(dept uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.department_officers d_o
    join public.profiles p on p.id = d_o.officer_id
    where d_o.department_id = dept
      and d_o.officer_id = auth.uid()
      and p.role = 'officer'
      and p.is_active = true
  );
$$;

-- Profiles policies
create policy "Users read own profile"
  on public.profiles for select
  using (auth.uid() = id or public.is_administrator());

create policy "Users update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Departments: read active for all authenticated; write admin only
create policy "Authenticated read active departments"
  on public.departments for select
  to authenticated
  using (is_active = true or public.is_administrator());

create policy "Admin manage departments"
  on public.departments for all
  using (public.is_administrator())
  with check (public.is_administrator());

-- Grievances: citizens own; officers via assignment/department; admins all
create policy "Citizen read own grievances"
  on public.grievances for select
  using (
    citizen_id = auth.uid()
    or public.is_administrator()
    or exists (
      select 1 from public.assignments a
      where a.grievance_id = grievances.id
        and a.is_current = true
        and (
          a.officer_id = auth.uid()
          or public.is_officer_of_department(a.department_id)
        )
    )
  );

create policy "Citizen insert own grievances"
  on public.grievances for insert
  with check (citizen_id = auth.uid());

create policy "Citizen update own draft grievances"
  on public.grievances for update
  using (
    citizen_id = auth.uid()
    and status in ('submitted', 'in_review')
  )
  with check (citizen_id = auth.uid());

create policy "Officer admin update grievances"
  on public.grievances for update
  using (
    public.is_administrator()
    or exists (
      select 1 from public.assignments a
      where a.grievance_id = grievances.id
        and a.is_current = true
        and (
          a.officer_id = auth.uid()
          or public.is_officer_of_department(a.department_id)
        )
    )
  );

-- Notifications: own only
create policy "User read own notifications"
  on public.notifications for select
  using (user_id = auth.uid());

create policy "User update own notifications"
  on public.notifications for update
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Audit logs: admin read only; inserts via service role / backend
create policy "Admin read audit logs"
  on public.audit_logs for select
  using (public.is_administrator());

-- Events, assignments, ai_analyses, attachments: mirror grievance visibility (simplified)
create policy "Read events for visible grievances"
  on public.grievance_events for select
  using (
    exists (
      select 1 from public.grievances g
      where g.id = grievance_events.grievance_id
        and (
          g.citizen_id = auth.uid()
          or public.is_administrator()
          or exists (
            select 1 from public.assignments a
            where a.grievance_id = g.id and a.is_current = true
              and (a.officer_id = auth.uid() or public.is_officer_of_department(a.department_id))
          )
        )
    )
  );

create policy "Read analyses for visible grievances"
  on public.ai_analyses for select
  using (
    exists (
      select 1 from public.grievances g
      where g.id = ai_analyses.grievance_id
        and (
          g.citizen_id = auth.uid()
          or public.is_administrator()
          or exists (
            select 1 from public.assignments a
            where a.grievance_id = g.id and a.is_current = true
              and (a.officer_id = auth.uid() or public.is_officer_of_department(a.department_id))
          )
        )
    )
  );

create policy "Read attachments for visible grievances"
  on public.attachments for select
  using (
    exists (
      select 1 from public.grievances g
      where g.id = attachments.grievance_id
        and (
          g.citizen_id = auth.uid()
          or public.is_administrator()
          or exists (
            select 1 from public.assignments a
            where a.grievance_id = g.id and a.is_current = true
              and (a.officer_id = auth.uid() or public.is_officer_of_department(a.department_id))
          )
        )
    )
  );

-- Note: INSERT/UPDATE on events, assignments, ai_analyses, attachments intended primarily
-- via FastAPI using service role or security definer functions in Phase 2.

comment on table public.grievances is 'Citizen grievances; official_* columns are human decisions.';
comment on table public.ai_analyses is 'AI suggestions only; not authoritative for resolution.';
