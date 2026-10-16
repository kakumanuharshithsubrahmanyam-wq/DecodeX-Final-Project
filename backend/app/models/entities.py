from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.enums import (
    AISource,
    GrievanceEventType,
    GrievanceStatus,
    IntakeChannel,
    NotificationChannel,
    PriorityLevel,
    UserRole,
)

# SQLite compatibility: use JSON instead of JSONB when needed
JsonType = JSON().with_variant(JSONB(), "postgresql")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(String(32), default=UserRole.citizen)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DepartmentOfficer(Base):
    __tablename__ = "department_officers"
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), primary_key=True
    )
    officer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GrievanceCategory(Base):
    __tablename__ = "grievance_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("grievance_categories.id"))
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    default_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Grievance(Base):
    __tablename__ = "grievances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location_text: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[GrievanceStatus] = mapped_column(String(32), default=GrievanceStatus.submitted)
    official_category: Mapped[Optional[str]] = mapped_column(Text)
    official_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    official_priority: Mapped[Optional[PriorityLevel]] = mapped_column(String(16))
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("grievance_categories.id"))
    subcategory_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("grievance_categories.id"))
    intake_channel: Mapped[IntakeChannel] = mapped_column(String(16), default=IntakeChannel.web)
    ward_or_locality: Mapped[Optional[str]] = mapped_column(Text)
    reopened_count: Mapped[int] = mapped_column(Integer, default=0)
    urgency_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    events: Mapped[list["GrievanceEvent"]] = relationship(back_populates="grievance")
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="grievance")
    sla: Mapped[Optional["GrievanceSLA"]] = relationship(back_populates="grievance", uselist=False)


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    unassigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    grievance: Mapped["Grievance"] = relationship(back_populates="assignments")


class GrievanceEvent(Base):
    __tablename__ = "grievance_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    event_type: Mapped[GrievanceEventType] = mapped_column(String(32))
    from_status: Mapped[Optional[GrievanceStatus]] = mapped_column(String(32))
    to_status: Mapped[Optional[GrievanceStatus]] = mapped_column(String(32))
    remark: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    grievance: Mapped["Grievance"] = relationship(back_populates="events")


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    __table_args__ = (UniqueConstraint("grievance_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[AISource] = mapped_column(String(16), default=AISource.rules)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_entities: Mapped[dict] = mapped_column(JsonType, default=dict)
    suggested_category: Mapped[Optional[str]] = mapped_column(Text)
    suggested_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    urgency_score: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    urgency_label: Mapped[PriorityLevel] = mapped_column(String(16), default=PriorityLevel.low)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    follow_up_questions: Mapped[list] = mapped_column(JsonType, default=list)
    detected_language: Mapped[Optional[str]] = mapped_column(String(8))
    provider_name: Mapped[Optional[str]] = mapped_column(String(64))
    provider_model: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_role: Mapped[str] = mapped_column(String(32), default="evidence")
    upload_status: Mapped[str] = mapped_column(String(16), default="pending")
    image_analysis: Mapped[Optional[dict]] = mapped_column(JsonType)
    exif_location_confirmed: Mapped[Optional[bool]] = mapped_column(Boolean)
    quality_flags: Mapped[list] = mapped_column(JsonType, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SLAPolicy(Base):
    __tablename__ = "sla_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[PriorityLevel] = mapped_column(String(16), nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("grievance_categories.id"))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    first_response_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GrievanceSLA(Base):
    __tablename__ = "grievance_sla"

    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"), primary_key=True)
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sla_policies.id"))
    first_response_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    breached_first_response: Mapped[bool] = mapped_column(Boolean, default=False)
    breached_resolution: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    grievance: Mapped["Grievance"] = relationship(back_populates="sla")


class CitizenFeedback(Base):
    __tablename__ = "citizen_feedback"
    __table_args__ = (UniqueConstraint("grievance_id", "citizen_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    citizen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    satisfaction_score: Mapped[Optional[int]] = mapped_column(SmallInteger)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    improvement_suggestion: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    grievance_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("grievances.id"))
    channel: Mapped[NotificationChannel] = mapped_column(String(16), default=NotificationChannel.in_app)
    dedupe_key: Mapped[Optional[str]] = mapped_column(String(128))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"), primary_key=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    web_push_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_campaigns_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    emergency_alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    locale: Mapped[str] = mapped_column(String(8), default="en")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    metadata_json: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
