import type { UiGrievance, UiPriority } from '@/lib/grievance-mapper';

export type Notice = { id: number; title: string; body: string; time: string; read: boolean };

const CATEGORIES = [
  'Water Supply',
  'Roads & Potholes',
  'Sanitation',
  'Electricity',
  'Streetlights',
  'Drainage',
  'Public Health',
  'Public Safety',
  'Environment',
  'Transport',
  'Other',
];

const deptFor = (cat: string) =>
  (
    {
      'Water Supply': 'Water Works',
      'Roads & Potholes': 'GHMC — Roads',
      Sanitation: 'GHMC — Sanitation',
      Electricity: 'TSSPDCL — Electricity',
      Streetlights: 'Street Lighting Cell',
      Drainage: 'Sewerage & Drainage',
      'Public Health': 'Public Health Department',
      'Public Safety': 'Public Safety Cell',
      Environment: 'Environment & Parks',
      Transport: 'Transport Department',
    } as Record<string, string>
  )[cat] || 'Human Verification Queue';

const OFFICERS = ['Ananya Rao', 'Kiran Reddy', 'Meera Sharma', 'Arjun Naidu', 'Sana Fatima', 'Vikram Kumar'];
const statuses = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved'] as const;

const seedTitles: [string, string, string, string][] = [
  ['Water leakage near apartment main gate', 'Water Supply', 'High', 'Madhapur'],
  ['Large pothole on the main road', 'Roads & Potholes', 'High', 'Kondapur'],
  ['Garbage not collected for four days', 'Sanitation', 'Medium', 'Kukatpally'],
  ['Streetlight not working on lane 4', 'Streetlights', 'Medium', 'Miyapur'],
  ['Open electrical wire near school entrance', 'Electricity', 'Critical', 'Ameerpet'],
  ['Sewage overflowing onto footpath', 'Drainage', 'High', 'LB Nagar'],
  ['Irregular drinking water supply', 'Water Supply', 'Medium', 'Uppal'],
  ['Road damaged after recent rain', 'Roads & Potholes', 'Medium', 'Gachibowli'],
  ['Mosquito breeding near stagnant water', 'Public Health', 'High', 'Nallakunta'],
  ['Tree branch blocking pedestrian path', 'Environment', 'Low', 'Begumpet'],
  ['Transformer sparking at junction', 'Electricity', 'Critical', 'Secunderabad'],
  ['Overflowing public dustbin', 'Sanitation', 'Medium', 'Mehdipatnam'],
  ['Flooding near bus stop after rain', 'Drainage', 'High', 'Dilsukhnagar'],
  ['Missing manhole cover on residential street', 'Drainage', 'Critical', 'Manikonda'],
  ['Water contamination concern in colony', 'Water Supply', 'High', 'Chandanagar'],
  ['Damaged footpath near hospital', 'Roads & Potholes', 'Medium', 'Himayatnagar'],
  ['Streetlight flickering at park entrance', 'Streetlights', 'Low', 'Jubilee Hills'],
  ['Illegal dumping beside lake', 'Environment', 'Medium', 'Durgam Cheruvu'],
  ['Bus stop shelter roof damaged', 'Transport', 'Low', 'Tarnaka'],
  ['Public tap leaking continuously', 'Water Supply', 'Medium', 'Tolichowki'],
  ['Garbage pile attracting stray animals', 'Sanitation', 'High', 'Moosapet'],
  ['Road sign fallen near intersection', 'Other', 'Low', 'Somajiguda'],
  ['Drain blocked causing bad odour', 'Drainage', 'Medium', 'Chaitanyapuri'],
  ['Electric pole leaning toward road', 'Electricity', 'Critical', 'Kompally'],
  ['Public park lights out after sunset', 'Streetlights', 'Low', 'Alwal'],
  ['Water tanker not reaching scheduled area', 'Water Supply', 'Medium', 'Attapur'],
  ['Construction debris blocking road', 'Sanitation', 'Medium', 'Financial District'],
  ['Broken public toilet facility', 'Public Health', 'Medium', 'Nampally'],
  ['Unsafe crossing near school', 'Public Safety', 'High', 'Habsiguda'],
  ['Damaged road divider after collision', 'Roads & Potholes', 'High', 'Malkajgiri'],
];

export const seedData: UiGrievance[] = seedTitles.map((s, i) => ({
  id: `RTGS-2026-${String(1001 + i).padStart(4, '0')}`,
  title: s[0],
  description: `Residents have reported ${s[0].toLowerCase()} in ${s[3]}, Hyderabad. Please inspect the location and take appropriate corrective action.`,
  category: s[1],
  department: deptFor(s[1]),
  priority: s[2] as UiPriority,
  status: statuses[(i * 3 + 1) % 5],
  location: `${s[3]}, Hyderabad, Telangana`,
  created: `2026-10-${String(1 + (i % 15)).padStart(2, '0')}`,
  deadline: `2026-10-${String(18 + (i % 10)).padStart(2, '0')}`,
  officer: OFFICERS[i % OFFICERS.length],
  remarks: i % 3 === 0 ? ['Demo record: initial triage completed.'] : [],
  citizen: `Citizen ${String.fromCharCode(65 + (i % 26))}`,
  confidence: 72 + ((i * 7) % 27),
  review: i % 7 === 0 || s[2] === 'Critical',
  attachments: [],
  apiBacked: false,
}));

export const seedNotices: Notice[] = [
  {
    id: 1,
    title: 'Water supply maintenance',
    body: 'Sample advisory for demo mode only — not an official notice.',
    time: '10 min ago',
    read: false,
  },
  {
    id: 2,
    title: 'Community clean-up drive',
    body: 'Sample community message in demo mode.',
    time: '1 hour ago',
    read: false,
  },
  {
    id: 3,
    title: 'Demo sample data',
    body: 'These records are fictional Hyderabad samples. They are not real citizen complaints.',
    time: 'Yesterday',
    read: true,
  },
];

export { CATEGORIES, deptFor, OFFICERS };
