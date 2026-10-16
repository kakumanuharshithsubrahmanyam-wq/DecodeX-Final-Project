from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import PriorityLevel


class FollowUpQuestion(BaseModel):
    id: str
    question: str
    required: bool = True


class LLMAnalysisOutput(BaseModel):
    summary: str = Field(..., min_length=10, max_length=600)
    suggested_category_code: str = Field(..., min_length=2, max_length=32)
    urgency_label: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_human_review: bool = True
    explanation: str = Field(..., min_length=10, max_length=800)
    follow_up_questions: list[FollowUpQuestion] = Field(default_factory=list)

    @field_validator("confidence")
    @classmethod
    def confidence_not_probability_claim(cls, v: float) -> float:
        return round(v, 4)


class AnalysisProvenance(BaseModel):
    source: Literal["rules", "llm", "hybrid"]
    provider_name: Optional[str] = None
    provider_model: Optional[str] = None
    detected_language: str = "en"
