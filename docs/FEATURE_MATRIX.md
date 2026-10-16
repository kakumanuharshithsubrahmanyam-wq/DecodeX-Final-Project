# RTGS Feature Matrix

Phase key: **MVP** | **Next** | **Future**

| Feature | Module | Primary roles | Phase | Backend deps | External deps | Acceptance criteria |
|---------|--------|---------------|-------|--------------|---------------|---------------------|
| Web grievance submit | A | Citizen | MVP | Grievances, categories, events, AI analyze | — | Valid JWT; reference ID returned; event `submitted` recorded |
| Unique reference ID | A,B | Citizen | MVP | Grievances | — | Format `RTGS-{YYYY}-{6}`; searchable |
| Category/subcategory taxonomy | A | All | MVP | `grievance_categories` | — | Official selection + AI suggestion both visible |
| AI completeness + follow-ups | A,D | Citizen | MVP | `ai_analyses`, rules pipeline | Optional LLM | Follow-up questions when vague; no auto-reject |
| Dept/category/priority recommend | A,D | Citizen, Officer | MVP | AI + departments | Optional LLM | Confidence + explanation; officer can override |
| Officer assignment | A | Officer, Platform admin | MVP | `assignments`, events | — | Assignment history; status → assigned |
| Status transitions + remarks | A | Officer | MVP | Events, state machine | — | Invalid transition returns 409 |
| SLA policy + deadlines | A,B | Citizen, Officer, Admin | MVP | `sla_policies`, `grievance_sla` | — | Due dates on create/assign; breach flags |
| Escalation (manual/overdue) | A | Officer, Admin | MVP | Events, notifications | — | Escalated status with reason |
| Citizen tracking timeline | B | Citizen | MVP | `grievance_events` | — | Ordered events; no internal-only notes exposed |
| SLA breach warnings (UI) | B | Citizen, Officer | MVP | SLA fields | — | Warning when past due; not claimed as “real-time” until tested |
| In-app notifications | H | All | MVP | `notifications` | — | Created on key transitions; read/unread |
| Notification preferences | H | Citizen | MVP | `notification_preferences` | — | User can toggle channels (delivery Next) |
| Citizen feedback (1 per case) | F | Citizen | MVP | `citizen_feedback` | — | Only after resolved/closed; no duplicate |
| Reopen / review request | A | Citizen | Next | Events, status rules | — | Reopen within policy; audit trail |
| Admin operational dashboard | A | Platform admin | MVP | Analytics queries | — | Counts by status, SLA compliance, dept workload |
| Attachment upload | A,E | Citizen, Officer | Next | Storage, attachments | Supabase Storage | Signed URL; size/type limits |
| Image advisory analysis | E | Citizen, Officer | Next | `attachments.image_analysis` | Optional vision API | Labeled advisory; EXIF confirm step |
| Duplicate/related detection | A | Officer, Admin | Next | `grievance_relations`, AI | Optional LLM | Suggestions only; human confirms |
| Rules Telugu/English detection | D | Citizen | Next | AI language module | Optional LLM | Locale stored; fallback English |
| AI chatbot (web) | D | Citizen | Next | Chat sessions, tools | Optional LLM | Confirm before submit; no other users’ data |
| Email/SMS/web push delivery | H | Citizen | Next | Delivery worker | SendGrid/Twilio/etc. | `notification_delivery_attempts` updated |
| WhatsApp intake + notify | C,H | Citizen | Future | `integration_events`, webhooks | WhatsApp Business provider | Same grievance pipeline |
| Voice intake | C | Citizen | Future | Speech-to-text adapter | STT provider | Transcript → normalized intake |
| Mobile PWA install | C | Citizen | Future | — | — | Responsive web first in MVP |
| Native mobile app | C | Citizen | Future | Same API | App stores | Out of scope until API stable |
| Supabase Realtime timeline | B | Citizen | Future | Realtime subscription | Supabase | Only after security review |
| Community forums | G | Citizen, Moderator | Future | community_* tables | — | Not before core grievance RLS proven |
| Service disruptions feed | H | Citizen | Future | `service_disruptions` | — | Read-only municipal content |
| Maintenance schedules | H | Citizen | Future | `maintenance_schedules` | — | Area-filtered announcements |
| Campaigns / awareness | G,H | Citizen, Admin | Future | `campaigns` | — | Opt-in via preferences |
| Worker-specific feedback | F | Citizen | Future | Extended feedback schema | — | Never auto-penalize; review workflow |
