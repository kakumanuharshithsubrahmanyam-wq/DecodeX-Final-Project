# RTGS API Contract (v1.1 — platform redesign)

**Status:** Specification only. Endpoints do not exist until implemented in Phase 2+.

Base URL: `{VITE_API_BASE_URL}/api/v1`

Phase tags: **[MVP]** | **[Next]** | **[Future]**

Protected routes require:

```
Authorization: Bearer <supabase_access_token>
Content-Type: application/json
```

## Conventions

### Envelope

Success (single): `{ "data": { ... } }`

Success (list): `{ "data": [ ... ], "meta": { "page", "page_size", "total" } }`

Errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Summary",
    "details": [{ "field": "description", "message": "Required" }]
  }
}
```

| HTTP | code |
|------|------|
| 400 | VALIDATION_ERROR |
| 401 | UNAUTHORIZED |
| 403 | FORBIDDEN |
| 404 | NOT_FOUND |
| 409 | CONFLICT (invalid state transition, duplicate feedback) |
| 422 | UNPROCESSABLE |
| 429 | RATE_LIMITED |
| 500 | INTERNAL_ERROR |

### Reference ID

`RTGS-{YYYY}-{6 alphanumeric}` — server-assigned on create.

### Grievance status (API)

`submitted` | `needs_information` | `under_review` | `assigned` | `in_progress` | `resolved` | `closed` | `reopened` | `escalated`

Legacy: `in_review` accepted on input, returned as `under_review` where possible.

### Roles (in `/me`)

`citizen` | `officer` | `department_administrator` | `platform_administrator` | `community_moderator`

Legacy: `administrator` → treat as `platform_administrator`.

### Pagination / filters

Query: `page`, `page_size` (max 100), `status`, `priority`, `department_id`, `category_id`, `assigned_to`, `from`, `to`, `q`, `sort`.

---

## Health

### GET `/health` **[MVP]**

Public.

**Response 200:** `{ "data": { "status": "ok", "service": "rtgs-api", "version": "string" } }`

---

## Authentication and profile

### GET `/me` **[MVP]**

Auth: any active user with profile.

**Response 200**

```json
{
  "data": {
    "id": "uuid",
    "email": "string",
    "full_name": "string | null",
    "phone": "string | null",
    "role": "citizen | officer | ...",
    "permissions": ["grievance:create", "..."],
    "department_ids": ["uuid"],
    "locale": "en",
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Errors:** 401, 404 (profile not provisioned).

### PATCH `/me` **[MVP]**

Auth: self. Cannot change `role`.

**Request:** `{ "full_name?", "phone?", "locale?" }` (`locale`: `en` | `te` planned)

### GET `/me/notification-preferences` **[MVP]**

**Response:** preferences object matching `notification_preferences` table.

### PUT `/me/notification-preferences` **[MVP]**

**Request:** channel toggles, quiet hours, consent flags.

**Validation:** `emergency_alerts_enabled` cannot be disabled for certain alert types (policy TBD).

---

## Categories

### GET `/categories` **[MVP]**

Auth: authenticated. Returns active taxonomy tree.

**Response:** `{ "data": [{ "id", "code", "name", "parent_id", "children": [] }] }`

### POST `/categories` **[Next]**

Role: `platform_administrator`.

### PATCH `/categories/{id}` **[Next]**

Role: `platform_administrator`.

---

## Grievances

### POST `/grievances` **[MVP]**

Role: `citizen`.

**Request**

```json
{
  "title": "string | null",
  "description": "string (min 20)",
  "location_text": "string",
  "latitude": "number | null",
  "longitude": "number | null",
  "category_id": "uuid | null",
  "subcategory_id": "uuid | null",
  "category_hint": "string | null",
  "ward_or_locality": "string | null",
  "intake_channel": "web | mobile_web"
}
```

**Response 201:** grievance + `reference_id`, `status: submitted`, embedded `sla` summary if computed.

**Side effects:** event `submitted`; optional async analyze job.

### GET `/grievances` **[MVP]**

Role-scoped list (citizen: own; officer: dept/assigned; platform admin: filtered all).

### GET `/grievances/{id}` **[MVP]**

Full detail: grievance, events, assignments, attachments meta, latest_analysis, sla, feedback (if permitted).

### PATCH `/grievances/{id}` **[MVP]**

**Citizen:** edit description/location when status in `submitted`, `needs_information`, `under_review`.

**Officer/admin:** official category, department, priority; optional remark (creates event).

**Request (officer):**

```json
{
  "official_category_id": "uuid",
  "official_department_id": "uuid",
  "official_priority": "low | medium | high | critical",
  "officer_remark": "string"
}
```

### POST `/grievances/{id}/submit-additional-info` **[MVP]**

Role: citizen owner. When status is `needs_information`.

**Request:** `{ "description?", "location_text?", "responses": [{ "question_id", "answer" }] }`

**Response:** updated grievance; may transition to `under_review`.

### POST `/grievances/{id}/transitions` **[MVP]**

Role: officer or platform/department admin (per transition).

**Request**

```json
{
  "to_status": "assigned | in_progress | ...",
  "remark": "string | null"
}
```

**Errors:** 409 if transition not allowed.

### POST `/grievances/{id}/reopen` **[Next]**

Role: citizen (policy window) or officer.

**Request:** `{ "reason": "string" }`

### GET `/grievances/{id}/track` **[MVP]**

Citizen-safe tracking view (no internal remarks).

**Response**

```json
{
  "data": {
    "reference_id": "string",
    "status": "string",
    "timeline": [{ "status", "label", "occurred_at", "public_message" }],
    "current_department": { "id", "name" } | null,
    "sla": {
      "first_response_due_at": "ISO8601 | null",
      "resolution_due_at": "ISO8601 | null",
      "breached": false,
      "warnings": ["resolution_overdue"]
    },
    "resolution_summary": "string | null"
  }
}
```

---

## AI

### POST `/grievances/{id}/analyze` **[MVP]**

Role: owner or authorized officer.

**Request:** `{ "force": false }`

**Response 200:** analysis object (see v1.0 shape): summary, entities, suggestions, urgency, confidence, `requires_human_review`, `follow_up_questions`, `source: rules | llm`.

### POST `/grievances/{id}/follow-up-responses` **[MVP]**

Role: citizen owner.

### POST `/grievances/{id}/analyze-images` **[Next]**

Role: owner or officer. Requires attachments.

**Response:** updates `attachments[].image_analysis` (advisory).

### GET `/grievances/{id}/related` **[Next]**

Role: officer/admin. Duplicate/related candidates with confidence.

---

## Assignments and escalation

### POST `/grievances/{id}/assignments` **[MVP]**

Role: officer (dept scope), `department_administrator`, `platform_administrator`.

**Request:** `{ "department_id", "officer_id": "uuid | null" }`

### POST `/grievances/{id}/escalate` **[MVP]**

**Request:** `{ "reason": "string" }`

---

## Attachments

### POST `/grievances/{id}/attachments/upload-url` **[Next]**

**Request:** `{ "file_name", "content_type", "size_bytes", "attachment_role": "evidence | before | after | resolution" }`

### POST `/grievances/{id}/attachments/{attachment_id}/complete` **[Next]**

### POST `/grievances/{id}/attachments/{attachment_id}/confirm-location` **[Next]**

Citizen confirms EXIF-suggested location (never auto-applied without confirm).

---

## Feedback

### POST `/grievances/{id}/feedback` **[MVP]**

Role: citizen owner; grievance `resolved` or `closed`.

**Request**

```json
{
  "rating": 1,
  "satisfaction_score": 1,
  "comment": "string | null",
  "improvement_suggestion": "string | null"
}
```

**Errors:** 409 if feedback already exists.

### GET `/grievances/{id}/feedback` **[MVP]**

Role: owner, officer on case, admin.

---

## Departments and officers

### GET `/departments` **[MVP]**

### POST `/departments` **[MVP]**

Role: `platform_administrator`.

### PATCH `/departments/{id}` **[MVP]**

### GET `/departments/{id}/officers` **[MVP]**

### PUT `/departments/{id}/officers` **[MVP]**

---

## SLA

### GET `/sla-policies` **[Next]**

Role: platform admin.

### POST `/sla-policies` **[Next]**

### GET `/grievances/{id}/sla` **[MVP]**

Embedded in detail/track; dedicated endpoint optional same shape.

---

## Notifications

### GET `/notifications` **[MVP]**

### POST `/notifications/{id}/read` **[MVP]**

### POST `/notifications/read-all` **[Next]**

---

## Chatbot (web)

### POST `/chat/sessions` **[Next]**

Creates ephemeral session linked to user.

### POST `/chat/sessions/{id}/messages` **[Next]**

**Request:** `{ "message": "string" }`

**Response:** assistant messages, optional `tool_calls` (draft grievance, status lookup).

### POST `/chat/sessions/{id}/confirm-grievance` **[Next]**

Confirms draft → `POST /grievances` equivalent.

---

## Integrations (webhooks)

### POST `/integrations/whatsapp/inbound` **[Future]**

Provider signature auth (no Supabase JWT). Normalizes to intake pipeline.

### POST `/integrations/voice/inbound` **[Future]**

---

## Community **[Future]**

### GET `/community/posts`

### POST `/community/posts`

### POST `/community/posts/{id}/comments`

### POST `/community/reports`

Role: `community_moderator` for moderation endpoints (TBD).

**Privacy:** no private grievance fields in public posts API.

---

## Municipal services **[Future]**

### GET `/services/disruptions`

Area-filtered read.

### GET `/services/maintenance-schedules`

### GET `/campaigns`

Active campaigns; respects notification marketing consent.

---

## Analytics

### GET `/analytics/overview` **[MVP]**

Role: `platform_administrator`, `department_administrator` (scoped).

**Response:** totals, by_status, by_priority, overdue_count, sla_compliance_rate, avg_resolution_hours, department_workload[].

### GET `/analytics/trends` **[Next]**

Time series; category trends.

### GET `/analytics/duplicate-clusters` **[Next]**

### GET `/analytics/audit-logs` **[MVP]**

Role: platform admin.

---

## Permissions matrix (summary)

| Endpoint group | Citizen | Officer | Dept admin | Platform admin |
|----------------|---------|---------|------------|----------------|
| Create grievance | ✓ | — | — | — |
| Track own | ✓ | — | — | — |
| Dept cases | — | ✓ | ✓ | ✓ |
| Transitions | — | ✓ | ✓ | ✓ |
| Categories CRUD | — | — | — | ✓ |
| Analytics | — | limited | dept | ✓ |
| Community | ✓ | — | — | mod role |

---

## Changelog

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | 2026-10-16 | Initial contract |
| 1.1.0 | 2026-10-16 | Platform redesign: lifecycle, roles, SLA, feedback, phased endpoints |
