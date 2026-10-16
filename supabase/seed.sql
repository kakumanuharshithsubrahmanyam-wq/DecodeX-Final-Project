-- Dev seed data (run manually after migrations in Phase 2)
-- Do not run against production without review.

insert into public.departments (name, code, description)
values
  ('Municipal Sanitation', 'SAN', 'Waste, drainage, and public cleanliness'),
  ('Roads and Transport', 'ROAD', 'Potholes, street lighting, traffic signals'),
  ('Water Supply', 'WATER', 'Drinking water and pipeline issues'),
  ('Electricity', 'POWER', 'Power outages and street electrical hazards'),
  ('Health Services', 'HEALTH', 'Public health facilities and sanitation complaints')
on conflict (code) do nothing;

-- Top-level categories (subcategories can be added in Phase 2+)
insert into public.grievance_categories (code, name, description, sort_order)
values
  ('SANITATION', 'Sanitation and waste', 'Garbage, dumping, drainage blockages', 10),
  ('ROADS', 'Roads and infrastructure', 'Potholes, footpaths, street damage', 20),
  ('WATER', 'Water supply', 'Leaks, quality, supply interruptions', 30),
  ('POWER', 'Electricity', 'Outages, exposed wiring, street lights', 40),
  ('HEALTH', 'Public health', 'Stray animals, fogging, clinic access', 50),
  ('OTHER', 'Other civic issues', 'General municipal issues pending classification', 99)
on conflict (code) do nothing;

-- Default SLA policies (hours) — illustrative dev defaults
insert into public.sla_policies (name, priority, first_response_hours, resolution_hours)
select v.name, v.priority::public.priority_level, v.first_response_hours, v.resolution_hours
from (values
  ('Default low', 'low', 72, 336),
  ('Default medium', 'medium', 48, 168),
  ('Default high', 'high', 24, 72),
  ('Default critical', 'critical', 4, 24)
) as v(name, priority, first_response_hours, resolution_hours)
where not exists (
  select 1 from public.sla_policies s where s.name = v.name and s.priority = v.priority::public.priority_level
);
