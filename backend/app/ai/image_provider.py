from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from app.config import get_settings


@dataclass
class ImageAnalysisResult:
    status: Literal["not_configured", "completed", "error"]
    suggested_category_code: Optional[str] = None
    visual_description: Optional[str] = None
    ocr_text: Optional[str] = None
    confidence: Optional[float] = None
    requires_human_review: bool = True
    message: str = ""


async def analyze_grievance_image(storage_path: str, content_type: str) -> ImageAnalysisResult:
    settings = get_settings()
    if not settings.ai_vision_provider or not settings.openai_api_key:
        return ImageAnalysisResult(
            status="not_configured",
            message="Image analysis provider is not configured. Predictions are not available.",
            requires_human_review=True,
        )
    # Vision integration boundary — no fabricated predictions without provider call.
    return ImageAnalysisResult(
        status="not_configured",
        message=f"Vision provider '{settings.ai_vision_provider}' is declared but not wired in this release.",
        requires_human_review=True,
    )
