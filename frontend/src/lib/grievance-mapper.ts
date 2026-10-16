import type { GrievanceDetail, GrievanceSummary } from './types';

export type UiPriority = 'Critical' | 'High' | 'Medium' | 'Low';
export type UiStatus =
  | 'Submitted'
  | 'Under Review'
  | 'Assigned'
  | 'In Progress'
  | 'Resolved'
  | 'Reopened'
  | 'Needs information';

export type UiGrievance = {
  id: string;
  uuid?: string;
  title: string;
  description: string;
  category: string;
  department: string;
  priority: UiPriority;
  status: UiStatus;
  location: string;
  created: string;
  deadline: string;
  officer: string;
  remarks: string[];
  citizen: string;
  confidence: number;
  review: boolean;
  attachments: string[];
  rating?: number;
  referenceId?: string;
  apiBacked?: boolean;
};

const priorityFromApi = (p: string | null | undefined): UiPriority => {
  const v = (p ?? 'medium').toLowerCase();
  if (v === 'critical') return 'Critical';
  if (v === 'high') return 'High';
  if (v === 'low') return 'Low';
  return 'Medium';
};

export const statusFromApi = (s: string): UiStatus => {
  const map: Record<string, UiStatus> = {
    submitted: 'Submitted',
    needs_information: 'Needs information',
    under_review: 'Under Review',
    in_review: 'Under Review',
    assigned: 'Assigned',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Resolved',
    reopened: 'Reopened',
    escalated: 'Under Review',
  };
  return map[s] ?? 'Submitted';
};

export const statusToApi = (s: UiStatus): string => {
  const map: Record<UiStatus, string> = {
    Submitted: 'submitted',
    'Needs information': 'needs_information',
    'Under Review': 'under_review',
    Assigned: 'assigned',
    'In Progress': 'in_progress',
    Resolved: 'resolved',
    Reopened: 'reopened',
  };
  return map[s] ?? 'submitted';
};

export function summaryToUi(g: GrievanceSummary, citizenLabel: string): UiGrievance {
  return {
    id: g.reference_id,
    uuid: g.id,
    referenceId: g.reference_id,
    title: g.title ?? g.description_preview.slice(0, 80),
    description: g.description_preview,
    category: '—',
    department: g.official_department_id ?? '—',
    priority: priorityFromApi(g.official_priority),
    status: statusFromApi(g.status),
    location: '—',
    created: g.created_at.slice(0, 10),
    deadline: g.updated_at.slice(0, 10),
    officer: '—',
    remarks: [],
    citizen: citizenLabel,
    confidence: g.urgency_score ?? 0,
    review: g.requires_human_review,
    attachments: [],
    apiBacked: true,
  };
}

export function detailToUi(
  g: GrievanceDetail,
  events: { message?: string; event_type?: string }[],
  citizenLabel: string,
): UiGrievance {
  const base = summaryToUi(g, citizenLabel);
  return {
    ...base,
    description: g.description,
    location: g.location_text,
    deadline: g.sla?.resolution_due_at?.slice(0, 10) ?? base.deadline,
    confidence: g.latest_analysis?.confidence ?? base.confidence,
    review: g.requires_human_review,
    remarks: events
      .filter((e) => e.message)
      .map((e) => e.message as string),
  };
}
