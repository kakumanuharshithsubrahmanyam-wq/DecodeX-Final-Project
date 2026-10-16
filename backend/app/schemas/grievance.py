from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import GrievanceStatus, IntakeChannel, PriorityLevel


class GrievanceCreate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str = Field(..., min_length=20)
    location_text: str = Field(..., min_length=5)
    latitude: float | None = None
    longitude: float | None = None
    category_id: UUID | None = None
    subcategory_id: UUID | None = None
    category_hint: str | None = None
    ward_or_locality: str | None = None
    intake_channel: IntakeChannel = IntakeChannel.web


class GrievanceUpdateCitizen(BaseModel):
    description: str | None = Field(None, min_length=20)
    location_text: str | None = Field(None, min_length=5)
    ward_or_locality: str | None = None

    model_config = {"extra": "ignore"}


class GrievanceUpdateOfficer(BaseModel):
    official_category: str | None = None
    official_department_id: UUID | None = None
    official_priority: PriorityLevel | None = None
    category_id: UUID | None = None
    officer_remark: str | None = None


class FollowUpResponseItem(BaseModel):
    question_id: str
    answer: str


class SubmitAdditionalInfo(BaseModel):
    description: str | None = Field(None, min_length=20)
    location_text: str | None = Field(None, min_length=5)
    responses: list[FollowUpResponseItem] = Field(default_factory=list)


class FollowUpResponsesBody(BaseModel):
    responses: list[FollowUpResponseItem]


class TransitionRequest(BaseModel):
    to_status: GrievanceStatus
    remark: str | None = None


class AssignmentRequest(BaseModel):
    department_id: UUID
    officer_id: UUID | None = None


class EscalateRequest(BaseModel):
    reason: str = Field(..., min_length=5)


class AnalyzeRequest(BaseModel):
    force: bool = False


class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    satisfaction_score: int | None = Field(None, ge=1, le=5)
    comment: str | None = None
    improvement_suggestion: str | None = None


class GrievanceSummary(BaseModel):
    id: UUID
    reference_id: str
    status: str
    title: str | None
    description_preview: str
    official_priority: str | None
    official_department_id: UUID | None
    citizen_id: UUID
    created_at: datetime
    updated_at: datetime
    urgency_score: float | None
    requires_human_review: bool

    model_config = {"from_attributes": True}


class SLASummary(BaseModel):
    first_response_due_at: datetime | None
    resolution_due_at: datetime | None
    breached: bool
    warnings: list[str]


class AIAnalysisOut(BaseModel):
    id: UUID
    grievance_id: UUID
    version: int
    source: str
    summary: str
    extracted_entities: dict
    suggested_category: str | None
    suggested_department_id: UUID | None
    urgency_score: float
    urgency_label: str
    confidence: float
    requires_human_review: bool
    explanation: str | None
    follow_up_questions: list
    created_at: datetime


class GrievanceDetail(BaseModel):
    id: UUID
    reference_id: str
    status: str
    title: str | None
    description: str
    location_text: str
    latitude: float | None
    longitude: float | None
    citizen_id: UUID
    category_id: UUID | None
    official_category: str | None
    official_department_id: UUID | None
    official_priority: str | None
    urgency_score: float | None
    requires_human_review: bool
    created_at: datetime
    updated_at: datetime
    sla: SLASummary | None = None
    latest_analysis: AIAnalysisOut | None = None
