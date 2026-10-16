-- Phase 2: extend admin helper for platform_administrator and department scope

create or replace function public.is_platform_administrator()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid()
      and is_active = true
      and role in ('administrator', 'platform_administrator')
  );
$$;

-- Backward-compatible alias used by existing policies
create or replace function public.is_administrator()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select public.is_platform_administrator();
$$;

create or replace function public.is_department_administrator()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid()
      and is_active = true
      and role = 'department_administrator'
  );
$$;

-- Allow citizens to update during needs_information / under_review (not only in_review)
drop policy if exists "Citizen update own draft grievances" on public.grievances;

create policy "Citizen update own draft grievances"
  on public.grievances for update
  using (
    citizen_id = auth.uid()
    and status in ('submitted', 'in_review', 'needs_information', 'under_review')
  )
  with check (citizen_id = auth.uid());

-- Platform admins may read all grievances (department admins use assignment path in API)
-- Grievance select policy already includes is_administrator()

comment on function public.is_platform_administrator is 'Trusted role check; never use JWT user_metadata.';
