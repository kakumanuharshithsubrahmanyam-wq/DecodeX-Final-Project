from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.ai.language import detect_language, normalize_text_preserve
from app.ai.llm_provider import analyze_with_llm
from app.ai.rules_engine import AnalysisResult, analyze_complaint
from app.ai.schemas import AnalysisProvenance
from app.config import get_settings
from app.models.enums import PriorityLevel


@dataclass
class PipelineResult:
    analysis: AnalysisResult
    provenance: AnalysisProvenance


def _merge_llm(rules: AnalysisResult, llm) -> AnalysisResult:
    if not llm:
        return rules
    urgency = PriorityLevel(llm.urgency_label)
    merged_questions = llm.follow_up_questions or rules.follow_up_questions
    if isinstance(merged_questions, list) and merged_questions and hasattr(merged_questions[0], "model_dump"):
        merged_questions = [q.model_dump() for q in merged_questions]
    return AnalysisResult(
        summary=llm.summary or rules.summary,
        missing_fields=rules.missing_fields,
        follow_up_questions=merged_questions if merged_questions else rules.follow_up_questions,
        suggested_category_code=llm.suggested_category_code or rules.suggested_category_code,
        suggested_category_name=rules.suggested_category_name,
        suggested_department_code=rules.suggested_department_code,
        urgency_score=Decimal(str(max(float(rules.urgency_score), llm.confidence * 0.9))),
        urgency_label=urgency if urgency != PriorityLevel.low else rules.urgency_label,
        confidence=Decimal(str(min(0.95, max(float(rules.confidence), llm.confidence)))),
        requires_human_review=rules.requires_human_review or llm.requires_human_review,
        explanation=f"{rules.explanation} LLM advisory: {llm.explanation}",
        extracted_entities={**rules.extracted_entities, "llm_suggested_category": llm.suggested_category_code},
    )


async def run_analysis_pipeline(description: str, location_text: str, ward: str | None) -> PipelineResult:
    settings = get_settings()
    original_description = normalize_text_preserve(description)
    language = detect_language(original_description, location_text)
    rules = analyze_complaint(original_description, location_text, ward, language=language)
    rules.extracted_entities["original_text_preserved"] = True
    rules.extracted_entities["detected_language"] = language

    provenance = AnalysisProvenance(source="rules", detected_language=language)
    llm_out = None
    if settings.ai_mode in {"llm", "hybrid"}:
        llm_out = await analyze_with_llm(original_description, location_text, language)
        if llm_out:
            rules = _merge_llm(rules, llm_out)
            provenance = AnalysisProvenance(
                source="hybrid" if settings.ai_mode == "hybrid" else "llm",
                provider_name="openai",
                provider_model=settings.ai_model or "gpt-4o-mini",
                detected_language=language,
            )
    return PipelineResult(analysis=rules, provenance=provenance)
