from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    citizen = "citizen"
    officer = "officer"
    department_administrator = "department_administrator"
    platform_administrator = "platform_administrator"
    administrator = "administrator"
    community_moderator = "community_moderator"


class GrievanceStatus(str, enum.Enum):
    submitted = "submitted"
    needs_information = "needs_information"
    under_review = "under_review"
    in_review = "in_review"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"
    reopened = "reopened"
    escalated = "escalated"


class PriorityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AISource(str, enum.Enum):
    rules = "rules"
    llm = "llm"


class GrievanceEventType(str, enum.Enum):
    status_change = "status_change"
    remark = "remark"
    assignment = "assignment"
    analysis = "analysis"
    attachment = "attachment"
    feedback = "feedback"


class IntakeChannel(str, enum.Enum):
    web = "web"
    mobile_web = "mobile_web"
    whatsapp = "whatsapp"
    voice = "voice"
    chatbot = "chatbot"
    api = "api"


class NotificationChannel(str, enum.Enum):
    in_app = "in_app"
    email = "email"
    sms = "sms"
    web_push = "web_push"
    whatsapp = "whatsapp"
