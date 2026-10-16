from __future__ import annotations

"""Rules-based grievance analysis — no external LLM required."""

from dataclasses import dataclass, field
from decimal import Decimal
import re

from app.models.enums import PriorityLevel


@dataclass
class CategoryRule:
    code: str
    name: str
    keywords: list[str]
    department_code: str


@dataclass
class AnalysisResult:
    summary: str
    missing_fields: list[str]
    follow_up_questions: list[dict]
    suggested_category_code: str | None
    suggested_category_name: str | None
    suggested_department_code: str | None
    urgency_score: Decimal
    urgency_label: PriorityLevel
    confidence: Decimal
    requires_human_review: bool
    explanation: str
    extracted_entities: dict = field(default_factory=dict)


URGENT_KEYWORDS = [
    "fire",
    "electrocution",
    "live wire",
    "gas leak",
    "collapse",
    "severe injury",
    "children trapped",
    "explosion",
    "drowning",
]

CATEGORY_RULES: list[CategoryRule] = [
    CategoryRule("SANITATION", "Sanitation and waste", ["garbage", "waste", "dump", "drain", "sewage", "sanitation"], "SAN"),
    CategoryRule("ROADS", "Roads and infrastructure", ["pothole", "road", "footpath", "pavement", "street", "traffic"], "ROAD"),
    CategoryRule("WATER", "Water supply", ["water", "pipeline", "leak", "tap", "drinking"], "WATER"),
    CategoryRule("POWER", "Electricity", ["power", "electric", "outage", "street light", "transformer", "wire"], "POWER"),
    CategoryRule("HEALTH", "Public health", ["stray", "mosquito", "fogging", "clinic", "health"], "HEALTH"),
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check_completeness(description: str, location_text: str, ward: str | None) -> list[str]:
    missing: list[str] = []
    desc = normalize_text(description)
    if len(desc) < 40:
        missing.append("detailed_description")
    if not location_text or len(location_text.strip()) < 5:
        missing.append("location")
    if not ward and not re.search(r"\b(ward|colony|street|road|area|near)\b", desc + " " + (location_text or "")):
        missing.append("locality_or_landmark")
    if not re.search(r"\b(since|days|weeks|months|yesterday|today|hours)\b", desc):
        missing.append("duration_or_timeline")
    return missing


def generate_follow_up_questions(missing: list[str]) -> list[dict]:
    mapping = {
        "detailed_description": ("desc_detail", "Can you describe exactly what happened and how it affects daily life?", True),
        "location": ("loc_detail", "Please provide the exact location or nearest landmark.", True),
        "locality_or_landmark": ("locality", "Which ward, colony, or landmark is closest to the issue?", True),
        "duration_or_timeline": ("duration", "How long has this problem been occurring?", False),
    }
    questions = []
    for m in missing:
        if m in mapping:
            qid, qtext, required = mapping[m]
            questions.append({"id": qid, "question": qtext, "required": required})
    return questions


def match_category(description: str) -> tuple[CategoryRule | None, Decimal]:
    desc = normalize_text(description)
    best: CategoryRule | None = None
    best_score = 0
    for rule in CATEGORY_RULES:
        score = sum(1 for kw in rule.keywords if kw in desc)
        if score > best_score:
            best_score = score
            best = rule
    if not best or best_score == 0:
        return None, Decimal("0.35")
    confidence = min(Decimal("0.95"), Decimal("0.45") + Decimal(best_score) * Decimal("0.12"))
    return best, confidence


def assess_urgency(description: str) -> tuple[Decimal, PriorityLevel, bool]:
    desc = normalize_text(description)
    human_review = False
    for kw in URGENT_KEYWORDS:
        if kw in desc:
            human_review = True
            return Decimal("0.92"), PriorityLevel.critical, human_review
    if re.search(r"\b(urgent|immediate|danger|unsafe|hazard)\b", desc):
        human_review = True
        return Decimal("0.78"), PriorityLevel.high, human_review
    if re.search(r"\b(blocked|overflow|no water|no power)\b", desc):
        return Decimal("0.55"), PriorityLevel.medium, False
    return Decimal("0.25"), PriorityLevel.low, False


def summarize(description: str, max_len: int = 280) -> str:
    text = re.sub(r"\s+", " ", description.strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def analyze_complaint(
    description: str,
    location_text: str,
    ward_or_locality: str | None = None,
) -> AnalysisResult:
    missing = check_completeness(description, location_text, ward_or_locality)
    follow_ups = generate_follow_up_questions(missing)
    category, cat_confidence = match_category(description)
    urgency_score, urgency_label, urgent_review = assess_urgency(description)

    confidence = cat_confidence
    if missing:
        confidence = min(confidence, Decimal("0.55"))
    requires_review = urgent_review or bool(missing) or confidence < Decimal("0.5")

    explanation_parts = []
    if category:
        explanation_parts.append(
            f"Keyword rules suggest category '{category.name}' (code {category.code}) "
            f"with confidence {cat_confidence}."
        )
    else:
        explanation_parts.append("No strong category keyword match; manual classification recommended.")
    if missing:
        explanation_parts.append(f"Missing information detected: {', '.join(missing)}.")
    if urgent_review:
        explanation_parts.append("Potentially urgent language detected — flagged for human review (not an emergency alert).")

    return AnalysisResult(
        summary=summarize(description),
        missing_fields=missing,
        follow_up_questions=follow_ups,
        suggested_category_code=category.code if category else "OTHER",
        suggested_category_name=category.name if category else "Other civic issues",
        suggested_department_code=category.department_code if category else None,
        urgency_score=urgency_score,
        urgency_label=urgency_label,
        confidence=confidence,
        requires_human_review=requires_review,
        explanation=" ".join(explanation_parts),
        extracted_entities={
            "locations": [location_text] if location_text else [],
            "issues": [category.name] if category else [],
            "keywords": [
                kw for kw in (category.keywords if category else []) if kw in normalize_text(description)
            ],
        },
    )
