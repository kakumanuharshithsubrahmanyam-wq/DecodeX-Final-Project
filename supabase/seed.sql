-- Dev seed data (run manually after migration in Phase 2)
-- Do not run against production without review.

insert into public.departments (name, code, description)
values
  ('Municipal Sanitation', 'SAN', 'Waste, drainage, and public cleanliness'),
  ('Roads and Transport', 'ROAD', 'Potholes, street lighting, traffic signals'),
  ('Water Supply', 'WATER', 'Drinking water and pipeline issues'),
  ('Electricity', 'POWER', 'Power outages and street electrical hazards'),
  ('Health Services', 'HEALTH', 'Public health facilities and sanitation complaints')
on conflict (code) do nothing;
