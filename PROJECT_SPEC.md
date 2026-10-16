# RTGS — Real-Time Governance Society

**Citizen-centric urban governance and AI-powered grievance redressal**

RTGS is a digital platform for transparent, accessible, efficient, and trackable civic grievance redressal and access to municipal services. It is designed for responsive web first, with an architecture that can later support native mobile apps and messaging channels (WhatsApp, voice, SMS).

**Disclaimer:** RTGS is a software platform under development. It must not be presented as an official government service or as integrated with a live government system unless that integration is explicitly authorized and implemented.

## Problem statement

Urban grievance channels receive incomplete complaints, vague descriptions, wrong categories, and inconsistent follow-up. Citizens lack visibility into progress. Departments struggle with prioritization, SLA compliance, and workload visibility.

## Product vision

Enable citizens to report civic problems through multiple channels, receive intelligent assistance, track progress, evaluate service quality, and participate in community improvement — while giving municipal departments tools to categorize, prioritize, assign, investigate, and resolve complaints with SLA monitoring and operational analytics.

## Design principles

1. **Citizen-first transparency** — reference IDs, timelines, and clear status language.
2. **Human authority** — officials decide; AI recommends with confidence and explanations.
3. **Single intake pipeline** — all channels normalize into one grievance workflow.
4. **Privacy by default** — no public exposure of addresses, attachments, or private grievance text.
5. **Modular integrations** — missing provider credentials must not block local development.
6. **Achievable MVP** — advanced channels and community features ship after core security.

## Feature modules (A–H)

| Module | Summary | MVP scope |
|--------|---------|-----------|
| **A — Grievance management** | Registration, categorization, assignment, SLA, feedback, reopen | Core MVP |
| **B — Real-time tracking** | Timeline, deadlines, SLA warnings | MVP (polling); Realtime optional later |
| **C — Multichannel intake** | Web, mobile web/PWA, WhatsApp, voice, chatbot | Web MVP; others staged |
| **D — AI chatbot** | NLU, Telugu/English, guided submission, status queries | Rules MVP; LLM optional |
| **E — Image analysis** | Category hints, OCR, EXIF with consent | Interface MVP; models next phase |
| **F — Citizen feedback** | Ratings, satisfaction, improvement suggestions | MVP |
| **G — Community engagement** | Forums, drives, announcements | Deferred until core secure |
| **H — Smart notifications** | Multi-channel alerts with preferences | In-app MVP; external channels staged |

Detailed module mapping: [docs/FEATURE_MATRIX.md](docs/FEATURE_MATRIX.md).

## User roles

| Role | Capabilities |
|------|----------------|
| **Citizen** | Own grievances, tracking, feedback, notification preferences, permitted community participation (future) |
| **Municipal officer** | Assigned cases, AI review, status/remarks, resolution evidence, escalation |
| **Department administrator** | Department workflows, assignments, queues, SLA compliance (next phase UI) |
| **Platform administrator** | Departments, roles, categories, SLA policies, analytics, audit |
| **Community moderator** | Moderate public content only; no default access to private grievances (future) |

Authorization is enforced in **FastAPI and PostgreSQL RLS**, not UI hiding alone.

## Grievance lifecycle

**Submitted → Needs Information | Under Review → Assigned → In Progress → Resolved → Closed**

Also: **Reopened**, **Escalated**. Backend validates transitions; see [docs/DATA_MODEL.md](docs/DATA_MODEL.md).

AI must not auto-reject grievances or change official status without human action.

## MVP scope (achievable first release)

- Citizen registration/login (Supabase Auth).
- Web grievance submission with category, location, optional evidence.
- AI-assisted completeness check and follow-up questions (rules-based minimum).
- Category, department, and priority **recommendations** with confidence.
- Officer assignment and status workflow with event history.
- SLA deadlines and overdue/escalation indicators.
- Citizen tracking timeline and in-app notifications.
- Post-resolution citizen feedback.
- Platform admin dashboard: workload, resolution times, SLA compliance (aggregate).

## Staged extensions (interfaces defined pre-integration)

- Telugu/English multilingual input and responses.
- Image analysis pipeline (advisory labels, OCR, EXIF with confirmation).
- Email, SMS, web push, WhatsApp notifications.
- WhatsApp and voice intake webhooks.
- AI chatbot with tool-gated draft grievance creation.
- Duplicate/related grievance detection.
- Community forums and municipal campaigns/service disruption feeds.
- Supabase Realtime for live timeline updates (after tested).

## AI safety

- Separate **guidance**, **AI recommendations**, and **verified official** data in UI and API.
- No fabricated policies, resolution dates, or other citizens’ case details.
- Emergency broadcasts only from verified/authorized sources — not AI suspicion.
- Prompt-injection awareness on free-text complaints, images, and future public posts.
- Human review for low-confidence or consequential recommendations.

## Success metrics (product)

- Time to usable reference ID after submit.
- Percentage of grievances meeting first-response SLA.
- Citizen satisfaction scores collected post-resolution.
- Officer override rate on AI category (feedback for tuning).
- Zero cross-tenant/cross-citizen data leaks in permission tests.

## Related documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system and AI design
- [docs/API_CONTRACT.md](docs/API_CONTRACT.md) — REST integration contract
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md) — entities and lifecycle
- [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) — external providers
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — four-phase delivery
