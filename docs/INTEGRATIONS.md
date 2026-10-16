# RTGS External Integrations

All integrations are **optional at runtime**. The backend exposes internal interfaces; if credentials are absent, features degrade gracefully (in-app only, rules-based AI, web intake only).

## Design pattern

```
Channel adapter → IntakeNormalizer → GrievanceService → (AI pipeline) → Persistence
                      ↑
              integration_events (audit, redacted payload)
```

Outbound notifications:

```
NotificationService → ChannelRouter → ProviderAdapter → delivery_attempts
                              ↑
                    notification_preferences + dedupe_key
```

## Intake channels

| Channel | Phase | Interface | Config (backend `.env`) |
|---------|-------|-----------|-------------------------|
| Web / mobile web | MVP | REST `POST /grievances` | — |
| Chatbot (web) | Next | REST `/chat/*` + tools | Optional LLM |
| WhatsApp | Future | Webhook `/integrations/whatsapp/inbound` | `WHATSAPP_*`, provider token |
| Voice | Future | Webhook or upload + STT | `STT_PROVIDER_*` |

**Common normalized intake DTO** (internal, not necessarily public):

- `description`, `location_text`, optional geo, `category_hint`, `channel`, `external_thread_id`, `locale`, `attachments[]`

All channels receive the same `reference_id` and validation rules.

## Notification providers

| Channel | Phase | Adapter responsibility |
|---------|-------|------------------------|
| In-app | MVP | Insert `notifications` row |
| Email | Next | SMTP or SendGrid/Mailgun |
| SMS | Next | Twilio or regional SMS API |
| Web push | Next | VAPID keys; browser subscription storage |
| WhatsApp | Future | Template messages via authorized Business API |

Requirements:

- **Consent** via `notification_preferences`.
- **Dedupe** using `notifications.dedupe_key`.
- **Rate limits** per user and channel.
- **Retries** with backoff; record in `notification_delivery_attempts`.
- **Quiet hours** respected except verified emergency alerts.

Emergency alerts: only from platform administrators or ingested authorized feeds — never from raw AI output.

## AI providers

| Capability | Phase | Interface | Fallback |
|------------|-------|-----------|----------|
| Text understanding | MVP | `TextAnalysisProvider` | Rules + keywords |
| Follow-up questions | MVP | same | Template questions by category |
| Summarization | MVP | same | Extractive truncation |
| Telugu/English | Next | `LanguageDetector` | Default `en` |
| Embeddings / duplicates | Next | `SimilarityProvider` | Trigram/reference match |
| Vision / OCR | Next | `ImageAnalysisProvider` | Skip with user message |
| Speech-to-text | Future | `TranscriptionProvider` | Manual transcript entry |

Providers are swappable behind Python protocols; no provider SDK in frontend.

## Storage

| Use | Phase | Notes |
|-----|-------|-------|
| Complaint evidence | **MVP (Phase 3)** | Private bucket `complaint-attachments`; backend signed upload/download URLs |
| Resolution before/after | Next | `attachment_role` = before/after |
| Public community media | Future | Separate bucket; moderation |

EXIF GPS: extract server-side only if policy allows; **never** publish raw coordinates in public APIs; citizen confirms location.

## WhatsApp (planned)

1. Inbound webhook verifies signature.
2. Map sender to citizen (linked phone on profile) or guest session flow.
3. Create draft grievance; confirm via template button/text.
4. Outbound status updates use approved templates only.

Do not implement until Phase 4+ unless explicitly scheduled.

## Local development without credentials

| Missing | Behavior |
|---------|----------|
| LLM API key | `AI_MODE=rules` |
| Email/SMS/WhatsApp | In-app notifications only |
| WhatsApp webhook | Web intake only |
| Vision API | Upload stored; analysis skipped with advisory message |

See `backend/.env.example` for placeholder variable names.
