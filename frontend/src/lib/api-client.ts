/**
 * Central FastAPI client — use from Claude UI screens.
 * Never send service-role keys; Bearer token from Supabase session only.
 */
import type { ApiErrorBody, GrievanceDetail, GrievanceSummary, MeProfile, NotificationItem, PaginatedMeta } from './types';
import { getAccessToken } from './auth';

const baseUrl = () => {
  const url = import.meta.env.VITE_API_BASE_URL as string;
  if (!url) throw new Error('VITE_API_BASE_URL is not configured');
  return url.replace(/\/$/, '');
};

export class ApiError extends Error {
  code: string;
  status: number;
  details: ApiErrorBody['error']['details'];

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.code = body.error.code;
    this.status = status;
    this.details = body.error.details;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = await getAccessToken();
  if (!token) {
    throw new ApiError(401, { error: { code: 'UNAUTHORIZED', message: 'Not signed in', details: [] } });
  }
  const res = await fetch(`${baseUrl()}${path}`, {
    ...options,
    signal: options.signal ?? AbortSignal.timeout(20000),
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers ?? {}),
    },
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (json?.error) throw new ApiError(res.status, json as ApiErrorBody);
    throw new ApiError(res.status, {
      error: { code: 'INTERNAL_ERROR', message: res.statusText || 'Request failed', details: [] },
    });
  }
  return json as T;
}

export const api = {
  health: () => fetch(`${baseUrl()}/api/v1/health`).then((r) => r.json()),

  me: () => request<{ data: MeProfile }>('/api/v1/me'),

  listGrievances: (params?: Record<string, string | number>) => {
    const q = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => q.set(k, String(v)));
    const qs = q.toString();
    return request<{ data: GrievanceSummary[]; meta: PaginatedMeta }>(
      `/api/v1/grievances${qs ? `?${qs}` : ''}`,
    );
  },

  createGrievance: (body: {
    description: string;
    location_text: string;
    title?: string;
    ward_or_locality?: string;
  }) =>
    request<{ data: GrievanceDetail }>('/api/v1/grievances', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getGrievance: (id: string) => request<{ data: { grievance: GrievanceDetail; events: unknown[] } }>(`/api/v1/grievances/${id}`),

  trackGrievance: (id: string) => request<{ data: unknown }>(`/api/v1/grievances/${id}/track`),

  analyzeGrievance: (id: string, force = false) =>
    request<{ data: unknown }>(`/api/v1/grievances/${id}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ force }),
    }),

  submitAdditionalInfo: (
    id: string,
    body: { description?: string; location_text?: string; responses?: { question_id: string; answer: string }[] },
  ) =>
    request<{ data: GrievanceDetail }>(`/api/v1/grievances/${id}/submit-additional-info`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  transition: (id: string, to_status: string, remark?: string) =>
    request<{ data: GrievanceDetail }>(`/api/v1/grievances/${id}/transitions`, {
      method: 'POST',
      body: JSON.stringify({ to_status, remark }),
    }),

  assign: (id: string, department_id: string, officer_id?: string) =>
    request<{ data: unknown }>(`/api/v1/grievances/${id}/assignments`, {
      method: 'POST',
      body: JSON.stringify({ department_id, officer_id: officer_id ?? null }),
    }),

  feedback: (id: string, body: { rating: number; satisfaction_score?: number; comment?: string }) =>
    request<{ data: unknown }>(`/api/v1/grievances/${id}/feedback`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  notifications: (page = 1) =>
    request<{ data: NotificationItem[]; meta: PaginatedMeta }>(`/api/v1/notifications?page=${page}`),

  markNotificationRead: (id: string) =>
    request<{ data: unknown }>(`/api/v1/notifications/${id}/read`, { method: 'POST' }),

  /** Attachment flow: upload-url → PUT file → complete */
  attachmentUploadUrl: (
    grievanceId: string,
    file: { file_name: string; content_type: string; size_bytes: number; attachment_role?: string },
  ) =>
    request<{ data: { attachment_id: string; upload_url: string; expires_at: string } }>(
      `/api/v1/grievances/${grievanceId}/attachments/upload-url`,
      { method: 'POST', body: JSON.stringify(file) },
    ),

  attachmentComplete: (grievanceId: string, attachmentId: string) =>
    request<{ data: { id: string; upload_status: string } }>(
      `/api/v1/grievances/${grievanceId}/attachments/${attachmentId}/complete`,
      { method: 'POST' },
    ),

  attachmentDownloadUrl: (grievanceId: string, attachmentId: string) =>
    request<{ data: { download_url: string; expires_at: string } }>(
      `/api/v1/grievances/${grievanceId}/attachments/${attachmentId}/download-url`,
    ),

  deptQueue: (page = 1) => request<{ data: GrievanceSummary[]; meta: PaginatedMeta }>(`/api/v1/dept/grievances?page=${page}`),

  analyticsOverview: () => request<{ data: unknown }>('/api/v1/analytics/overview'),
};

/** Upload binary to signed URL returned by attachmentUploadUrl */
export async function uploadToSignedUrl(uploadUrl: string, file: Blob, contentType: string): Promise<Response> {
  return fetch(uploadUrl, {
    method: 'PUT',
    headers: { 'Content-Type': contentType },
    body: file,
  });
}
