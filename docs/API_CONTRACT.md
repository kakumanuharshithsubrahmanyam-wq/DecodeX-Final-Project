# RTGS API Contract (v1)

Base URL: `{VITE_API_BASE_URL}/api/v1`

All protected endpoints require:

```
Authorization: Bearer <supabase_access_token>
Content-Type: application/json
```

## Conventions

### Success responses

Single resource:

```json
{
  "data": { }
}
```

List with pagination:

```json
{
  "data": [ ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 42
  }
}
```

### Timestamps

ISO 8601 in UTC, e.g. `"2026-10-16T06:48:00Z"`.

### Grievance reference ID

Format: `RTGS-{YYYY}-{6 alphanumeric}` — assigned by server on create.

### Error envelope

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable summary",
    "details": [
      { "field": "description", "message": "Required" }
    ]
  }
}
```

| HTTP | code | When |
|------|------|------|
| 400 | VALIDATION_ERROR | Invalid body or query |
| 401 | UNAUTHORIZED | Missing or invalid JWT |
| 403 | FORBIDDEN | Valid user, insufficient role/scope |
| 404 | NOT_FOUND | Resource missing or not visible |
| 409 | CONFLICT | Illegal state transition |
| 422 | UNPROCESSABLE | Semantic validation (e.g. closed grievance) |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Unexpected server failure |

Frontend expectations:

- **Loading:** show skeleton/spinner; disable submit buttons.
- **Empty lists:** show guided empty state (e.g. “No grievances yet”).
- **401:** redirect to login / refresh session.
- **403/404:** non-destructive message; no data leakage across roles.

### Filtering and sorting (lists)

Query params (where supported):

- `status`, `priority`, `department_id`, `assigned_to`, `from`, `to` (ISO dates)
- `q` — full-text search on reference_id and description (officer/admin)
- `sort` — e.g. `-created_at`, `urgency_score`
- `page`, `page_size` (default 20, max 100)

---

## Authentication and profile

### GET `/health`

Public. No auth.

**Response 200**

```json
{
  "data": {
    "status": "ok",
    "service": "rtgs-api",
    "version": "0.1.0"
  }
}
```

### GET `/me`

**Role:** any authenticated user with profile.

**Response 200**

```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "string | null",
    "role": "citizen | officer | administrator",
    "phone": "string | null",
    "department_ids": ["uuid"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Errors:** 401 if token invalid; 404 if auth user exists but profile not provisioned.

### PATCH `/me`

**Role:** self.

**Request**

```json
{
  "full_name": "string",
  "phone": "string"
}
```

**Response 200:** same shape as GET `/me`.

**Validation:** phone format optional E.164; cannot change `role` via this endpoint.

---

## Grievances

### POST `/grievances`

**Role:** citizen (administrator may create on behalf in Phase 3+ — not MVP).

**Request**

```json
{
  "title": "string (optional, max 200)",
  "description": "string (required, min 20)",
  "location_text": "string (required)",
  "latitude": 17.3850,
  "longitude": 78.4867,
  "category_hint": "string | null"
}
```

**Response 201**

```json
{
  "data": {
    "id": "uuid",
    "reference_id": "RTGS-2026-ABC123",
    "status": "submitted",
    "title": "string | null",
    "description": "string",
    "location_text": "string",
    "latitude": "number | null",
    "longitude": "number | null",
    "citizen_id": "uuid",
    "official_category": "string | null",
    "official_department_id": "uuid | null",
    "official_priority": "low | medium | high | critical | null",
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "latest_analysis": null
  }
}
```

Side effect: creates initial `grievance_events` entry (`submitted`); may enqueue async analysis (Phase 3).

### GET `/grievances`

**Role:**

- **citizen:** own grievances only.
- **officer:** assigned or department-scoped.
- **administrator:** all (with filters).

**Response 200:** paginated list of grievance summary objects:

```json
{
  "id": "uuid",
  "reference_id": "RTGS-2026-ABC123",
  "status": "submitted | in_review | assigned | in_progress | resolved | closed | escalated",
  "title": "string | null",
  "description_preview": "first 160 chars",
  "official_priority": "low | medium | high | critical | null",
  "official_department_id": "uuid | null",
  "citizen_id": "uuid",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "urgency_score": "number | null",
  "requires_human_review": "boolean"
}
```

### GET `/grievances/{grievance_id}`

**Role:** citizen (owner), assigned officer, or admin.

**Response 200**

```json
{
  "data": {
    "grievance": { },
    "events": [
      {
        "id": "uuid",
        "event_type": "status_change | remark | assignment | analysis",
        "from_status": "string | null",
        "to_status": "string | null",
        "remark": "string | null",
        "actor_id": "uuid",
        "created_at": "ISO8601"
      }
    ],
    "assignments": [
      {
        "id": "uuid",
        "department_id": "uuid",
        "officer_id": "uuid | null",
        "assigned_at": "ISO8601",
        "unassigned_at": "ISO8601 | null"
      }
    ],
    "attachments": [
      {
        "id": "uuid",
        "file_name": "string",
        "content_type": "string",
        "size_bytes": 12345,
        "storage_path": "string",
        "created_at": "ISO8601"
      }
    ],
    "latest_analysis": { }
  }
}
```

### PATCH `/grievances/{grievance_id}`

**Role:** citizen (limited) or officer/admin.

**Citizen request** (only while `status` in `submitted`, `in_review`):

```json
{
  "description": "string",
  "location_text": "string"
}
```

**Officer/admin request**

```json
{
  "official_category": "string",
  "official_department_id": "uuid",
  "official_priority": "low | medium | high | critical",
  "status": "in_review | assigned | in_progress | resolved | closed | escalated",
  "officer_remark": "string"
}
```

**Response 200:** full grievance object.

**Errors:** 409 on invalid transitions; 422 if resolved/closed and citizen tries to edit.

---

## AI analysis and follow-up

### POST `/grievances/{grievance_id}/analyze`

**Role:** citizen (owner) or officer/admin.

Triggers (re)analysis. Idempotent within cooldown (e.g. 60s) — returns latest if recent.

**Request** (optional)

```json
{
  "force": false
}
```

**Response 200**

```json
{
  "data": {
    "id": "uuid",
    "grievance_id": "uuid",
    "version": 1,
    "source": "rules | llm",
    "summary": "string",
    "extracted_entities": {
      "locations": ["string"],
      "issues": ["string"],
      "keywords": ["string"]
    },
    "suggested_category": "string | null",
    "suggested_department_id": "uuid | null",
    "urgency_score": 0.0,
    "urgency_label": "low | medium | high | critical",
    "confidence": 0.0,
    "requires_human_review": true,
    "explanation": "string",
    "follow_up_questions": [
      {
        "id": "string",
        "question": "string",
        "required": true
      }
    ],
    "created_at": "ISO8601"
  }
}
```

### POST `/grievances/{grievance_id}/follow-up-responses`

**Role:** citizen (owner).

**Request**

```json
{
  "responses": [
    { "question_id": "string", "answer": "string" }
  ]
}
```

**Response 200:** new or updated `latest_analysis` (may trigger re-analysis).

---

## Assignments and status

### POST `/grievances/{grievance_id}/assignments`

**Role:** officer (within dept) or administrator.

**Request**

```json
{
  "department_id": "uuid",
  "officer_id": "uuid | null"
}
```

**Response 201:** assignment object; grievance status typically moves to `assigned`.

### POST `/grievances/{grievance_id}/escalate`

**Role:** officer or administrator.

**Request**

```json
{
  "reason": "string (required)"
}
```

**Response 200:** updated grievance with `status: escalated`.

---

## Departments and officers (admin)

### GET `/departments`

**Role:** authenticated (citizens see active list for hints; officers see own).

**Response 200:** paginated `{ id, name, code, description, is_active }`.

### POST `/departments`

**Role:** administrator.

**Request:** `{ "name", "code", "description" }`

### PATCH `/departments/{department_id}`

**Role:** administrator.

### GET `/departments/{department_id}/officers`

**Role:** administrator.

### PUT `/departments/{department_id}/officers`

**Role:** administrator.

**Request**

```json
{
  "officer_ids": ["uuid"]
}
```

---

## Attachments

### POST `/grievances/{grievance_id}/attachments/upload-url`

**Role:** citizen (owner) or officer.

**Request**

```json
{
  "file_name": "photo.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 1048576
}
```

**Response 200**

```json
{
  "data": {
    "attachment_id": "uuid",
    "upload_url": "signed url",
    "expires_at": "ISO8601"
  }
}
```

Client uploads via PUT to signed URL; then optional `POST .../attachments/{id}/complete`.

---

## Notifications

### GET `/notifications`

**Role:** self.

**Response 200:** paginated `{ id, type, title, body, read_at, created_at, grievance_id }`.

### POST `/notifications/{notification_id}/read`

**Role:** self.

**Response 200:** `{ "data": { "id", "read_at" } }`

---

## Dashboard analytics

### GET `/analytics/overview`

**Role:** administrator.

**Query:** `from`, `to` (ISO date).

**Response 200**

```json
{
  "data": {
    "total_grievances": 0,
    "by_status": { "submitted": 0 },
    "by_priority": { "high": 0 },
    "overdue_count": 0,
    "avg_resolution_hours": null,
    "department_workload": [
      { "department_id": "uuid", "open_count": 0, "overdue_count": 0 }
    ]
  }
}
```

### GET `/analytics/audit-logs`

**Role:** administrator.

Paginated audit entries: `{ actor_id, action, resource_type, resource_id, metadata, created_at }`.

---

## Webhooks / realtime (future)

Not in MVP. Notifications may later use Supabase Realtime on `notifications` table.

---

## Changelog

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | 2026-10-16 | Phase 1 draft contract |
