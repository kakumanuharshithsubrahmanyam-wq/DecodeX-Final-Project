# RTGS Data Model Plan

Schema sources (apply in order):

1. `supabase/migrations/20251016120000_initial_schema.sql`
2. `supabase/migrations/20251016130000_platform_redesign_extensions.sql`

**Legend:** MVP = core delivery | Next = following feature phases | Future = optional expansion

## Entity classification

| Entity | Phase | Purpose |
|--------|-------|---------|
| `profiles` | MVP | Identity, role, contact; 1:1 with Supabase Auth |
| `departments` | MVP | Municipal departments |
| `department_officers` | MVP | Officer ↔ department membership |
| `grievance_categories` | MVP | Validated category/subcategory taxonomy |
| `grievances` | MVP | Core complaint record + official decisions |
| `assignments` | MVP | Department/officer responsibility history |
| `grievance_events` | MVP | **Source of truth** for status timeline |
| `grievance_sla` | MVP | Per-case deadlines and breach flags |
| `sla_policies` | MVP | Configurable SLA rules by priority/category/dept |
| `ai_analyses` | MVP | Versioned AI suggestions (not official facts) |
| `attachments` | MVP | Storage metadata; optional `image_analysis` JSON |
| `citizen_feedback` | MVP | Post-resolution ratings and comments |
| `notifications` | MVP | In-app inbox (+ channel, dedupe_key) |
| `notification_preferences` | MVP | Consent and channel toggles |
| `audit_logs` | MVP | Security and admin actions |
| `grievance_relations` | Next | Duplicate/related case linking |
| `notification_delivery_attempts` | Next | Provider delivery observability |
| `integration_events` | Next | Multichannel intake/outbound audit |
| `community_posts` | Future | Public forums (not before core workflow is secure) |
| `community_comments` | Future | Threaded discussion |
| `community_reports` | Future | Moderation reports |
| `service_disruptions` | Future | Area service outage announcements |
| `maintenance_schedules` | Future | Planned maintenance |
| `campaigns` | Future | Awareness / municipal campaigns |

Community and municipal broadcast tables are **specified in API/docs only** until Phase 4+; no DDL until grievance RLS and officer workflows are proven.

## Roles (`profiles.role`)

| Role | MVP | Notes |
|------|-----|-------|
| `citizen` | Yes | Default on signup |
| `officer` | Yes | Municipal case worker |
| `department_administrator` | Next | Department queues, assignments, SLA view |
| `platform_administrator` | Yes | Full config; legacy enum value `administrator` treated as alias in app |
| `community_moderator` | Future | Community content only; **no** default access to private grievances |

Roles are assigned only via trusted server paths (service role / platform admin API), never from JWT `user_metadata`.

## Grievance lifecycle

Canonical statuses (enum):

| Status | Meaning |
|--------|---------|
| `submitted` | Received; may await AI or triage |
| `needs_information` | Citizen must supply missing details |
| `under_review` | Municipal triage (legacy `in_review` mapped in API) |
| `assigned` | Department/officer assigned |
| `in_progress` | Active investigation/work |
| `resolved` | Work completed; may await feedback |
| `closed` | Terminal; no further work expected |
| `reopened` | Citizen or official reopened after resolve/close |
| `escalated` | Overdue or manual escalation |

### Permitted transitions (backend must validate)

```
submitted → needs_information | under_review | assigned
needs_information → under_review | submitted (if re-submitted)
under_review → needs_information | assigned | escalated
assigned → in_progress | needs_information | escalated
in_progress → resolved | needs_information | escalated
resolved → closed | reopened
closed → reopened (within policy window)
reopened → under_review | assigned | in_progress
escalated → assigned | in_progress | resolved
```

AI **must not** transition status or reject submissions.

## Key fields and separation

| Concern | Official (human) | AI (advisory) |
|---------|-------------------|---------------|
| Category | `grievances.category_id`, `official_category` | `ai_analyses.suggested_category`, suggested category_id |
| Department | `official_department_id` | `ai_analyses.suggested_department_id` |
| Priority | `official_priority` | `urgency_label`, `urgency_score` on analysis |

Denormalized `grievances.urgency_score` / `requires_human_review` exist for list performance; refresh from latest analysis on write.

## Indexes and retention (plan)

| Data | Retention guidance |
|------|-------------------|
| `grievance_events`, `audit_logs` | Long-lived; legal/ops policy TBD |
| `integration_events.payload_summary` | Store redacted summaries; raw payloads in provider systems |
| `ai_analyses` | Retain all versions for audit |
| Attachments | Citizen deletion requests handled per policy; storage lifecycle rules in Phase 4 |
| Community content | Soft-delete + moderator audit when implemented |

## Authorization summary

- **Citizen:** CRUD own grievances (limited fields); read own timeline, SLA, feedback.
- **Officer:** Read/update assigned or department-scoped grievances.
- **Department administrator:** Department assignment and SLA dashboards (Next).
- **Platform administrator:** Categories, departments, roles, analytics, audit.
- **Community moderator:** Community tables only (Future).

RLS on all public tables; backend uses user-scoped JWT where appropriate and **controlled** service role for orchestration (notifications, integration webhooks) with explicit checks — not blanket bypass.

See `ARCHITECTURE.md` for FastAPI JWT verification and storage access.
