# RTGS — Real-Time Governance Society

## Problem statement

Government grievance portals receive incomplete complaints, vague descriptions, and incorrectly categorized submissions. These failures delay routing, assignment, and resolution.

## Objectives

- Help citizens submit understandable, actionable grievances.
- Detect missing information and ask contextual follow-up questions.
- Extract facts (location, issue type, entities) without altering citizen intent.
- Recommend responsible departments and categories with explainable confidence.
- Assess urgency using transparent, auditable rules.
- Track assignments, status changes, and resolution deadlines.
- Give officers AI-assisted summaries and administrative tools (human decisions remain authoritative).
- Give administrators operational visibility, audit trails, and analytics.

## AI safety and scope

The AI **assists** authorized officials. It must **not**:

- Automatically reject grievances.
- Present AI inferences as verified facts or official decisions.
- Make unsupported claims about danger, legality, or guaranteed resolution.

All recommendations are labeled as suggestions; officers and administrators may override with audit logging.

## User roles

| Role | Description |
|------|-------------|
| **Citizen** | Submits and tracks own grievances; answers follow-ups; provides feedback. |
| **Officer** | Works assigned cases in authorized departments; updates status and remarks. |
| **Administrator** | Manages departments, officer assignments, and cross-cutting visibility within policy. |

Role is stored server-side (`profiles.role` and department links), not in user-editable JWT metadata.

## Core features (MVP)

### Citizen

- Register and log in (Supabase Auth).
- Create grievance with description, location, optional attachments.
- Answer AI follow-up questions.
- View suggested category, department, and priority (as recommendations).
- Track reference ID, status, assigned department, timestamps.
- Receive in-app notifications for status changes.
- Submit feedback or request review.

### Government officer

- List and open cases assigned to self or department (per policy).
- Review AI analysis, confidence, and explanations.
- Correct category, department, and priority; add official remarks.
- Update status and upload resolution evidence.
- Escalate overdue or high-urgency cases.

### Administrator

- CRUD departments; assign officers to departments.
- Filter and view grievances permitted by role.
- Monitor pending, overdue, and urgent queues.
- View workload and resolution analytics.
- Inspect audit trail and classification corrections.

### AI engine (modular pipeline)

- Completeness and vagueness detection.
- Follow-up question generation.
- Neutral summarization.
- Entity and location extraction.
- Category and department recommendation.
- Explainable urgency score with confidence; flag low-confidence for human review.
- **Baseline:** rules-based path when no external LLM credentials are configured.

## MVP scope (Phase 2–4)

Included in accelerated delivery:

- End-to-end grievance submit → analyze → assign → resolve flow.
- Supabase Auth + FastAPI JWT validation.
- PostgreSQL schema with RLS for citizen-owned data.
- Officer and admin dashboards (Claude UI + Cursor backend).
- Rules-based AI with optional LLM upgrade hook.

## Deferred (post-MVP)

- Duplicate complaint detection.
- Multilingual support (Telugu + English priority).
- SLA breach alerts and escalation automation.
- Geographic complaint hotspots.
- Public aggregate transparency reports.
- SMS/email notification providers beyond in-app.

## Success criteria (product)

- Citizens receive a unique reference ID within one submission session.
- Every status change is recorded in `grievance_events` with actor and timestamp.
- Officers can always distinguish AI suggestions from official fields.
- Administrators can explain backlog and overdue counts from dashboard metrics.
