/** Shared API types aligned with docs/API_CONTRACT.md — adjust when OpenAPI is generated. */

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: { field?: string; message: string }[];
  };
};

export type PaginatedMeta = {
  page: number;
  page_size: number;
  total: number;
};

export type MeProfile = {
  id: string;
  email: string;
  full_name: string | null;
  phone: string | null;
  role: string;
  permissions: string[];
  department_ids: string[];
  locale: string;
};

export type GrievanceSummary = {
  id: string;
  reference_id: string;
  status: string;
  title: string | null;
  description_preview: string;
  official_priority: string | null;
  official_department_id: string | null;
  citizen_id: string;
  urgency_score: number | null;
  requires_human_review: boolean;
  created_at: string;
  updated_at: string;
};

export type AIAnalysis = {
  id: string;
  grievance_id: string;
  version: number;
  source: 'rules' | 'llm';
  summary: string;
  suggested_category: string | null;
  suggested_department_id: string | null;
  urgency_score: number;
  urgency_label: string;
  confidence: number;
  requires_human_review: boolean;
  explanation: string | null;
  follow_up_questions: { id: string; question: string; required: boolean }[];
};

export type GrievanceDetail = GrievanceSummary & {
  description: string;
  location_text: string;
  latest_analysis?: AIAnalysis | null;
  sla?: {
    first_response_due_at: string | null;
    resolution_due_at: string | null;
    breached: boolean;
    warnings: string[];
  } | null;
};

export type NotificationItem = {
  id: string;
  type: string;
  title: string;
  body: string;
  grievance_id: string | null;
  read_at: string | null;
  created_at: string;
};
