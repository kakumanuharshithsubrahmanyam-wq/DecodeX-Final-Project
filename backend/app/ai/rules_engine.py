from __future__ import annotations

"""Rules-based grievance analysis — no external LLM required."""

from dataclasses import dataclass, field
from decimal import Decimal
import re

from app.ai.keywords_te import TELUGU_CATEGORY_KEYWORDS, TELUGU_FOLLOW_UPS, TELUGU_URGENT
from app.ai.language import TELUGU_RANGE
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

VAGUE_PATTERNS = [
    r"^\s*(bad|issue|problem|help|fix this)\s*$",
    r"\b(something|anything|stuff)\b",
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check_completeness(description: str, location_text: str, ward: str | None, language: str = "en") -> list[str]:
    missing: list[str] = []
    desc = description.strip()
    desc_norm = normalize_text(description)
    if len(desc) < 40 or any(re.search(p, desc_norm) for p in VAGUE_PATTERNS):
        missing.append("detailed_description")
    if not location_text or len(location_text.strip()) < 5:
        missing.append("location")
    loc_hints_en = r"\b(ward|colony|street|road|area|near)\b"
    loc_hints_te = r"(వార్డ్|కాలనీ|రోడ్|దగ్గర)"
    combined = desc + " " + (location_text or "")
    if not ward and not re.search(loc_hints_en, combined, re.I) and not re.search(loc_hints_te, combined):
        missing.append("locality_or_landmark")
    duration_en = r"\b(since|days|weeks|months|yesterday|today|hours)\b"
    duration_te = r"(రోజుల|నెల|week|month|yesterday|today)"
    if not re.search(duration_en, desc_norm) and not re.search(duration_te, desc, re.I):
        missing.append("duration_or_timeline")
    if language == "te" and len(TELUGU_RANGE.findall(desc)) < 2 and len(desc) < 60:
        missing.append("detailed_description")
    return missing


def generate_follow_up_questions(missing: list[str], language: str = "en") -> list[dict]:
    mapping_en = {
        "detailed_description": ("desc_detail", "Can you describe exactly what happened and how it affects daily life?", True),
        "location": ("loc_detail", "Please provide the exact location or nearest landmark.", True),
        "locality_or_landmark": ("locality", "Which ward, colony, or landmark is closest to the issue?", True),
        "duration_or_timeline": ("duration", "How long has this problem been occurring?", False),
    }
    questions = []
    for m in missing:
        if language in {"te", "mixed"} and m in TELUGU_FOLLOW_UPS:
            qid, qtext, required = TELUGU_FOLLOW_UPS[m]
            questions.append({"id": qid, "question": qtext, "required": required})
        elif m in mapping_en:
            qid, qtext, required = mapping_en[m]
            questions.append({"id": qid, "question": qtext, "required": required})
    return questions


def match_category(description: str, language: str = "en") -> tuple[CategoryRule | None, Decimal]:
    desc = normalize_text(description)
    raw = description
    best: CategoryRule | None = None
    best_score = 0
    for rule in CATEGORY_RULES:
        score = sum(1 for kw in rule.keywords if kw in desc)
        if language in {"te", "mixed"}:
            te_kws = TELUGU_CATEGORY_KEYWORDS.get(rule.code, [])
            score += sum(1 for kw in te_kws if kw in raw or kw in desc)
        if score > best_score:
            best_score = score
            best = rule
    if not best or best_score == 0:
        return None, Decimal("0.35")
    confidence = min(Decimal("0.95"), Decimal("0.45") + Decimal(best_score) * Decimal("0.12"))
    return best, confidence


def assess_urgency(description: str, language: str = "en") -> tuple[Decimal, PriorityLevel, bool]:
    desc = normalize_text(description)
    raw = description
    human_review = False
    urgent_terms = list(URGENT_KEYWORDS)
    if language in {"te", "mixed"}:
        urgent_terms.extend(TELUGU_URGENT)
    for kw in urgent_terms:
        if kw in desc or kw in raw:
            human_review = True
            return Decimal("0.92"), PriorityLevel.critical, human_review
    if re.search(r"\b(urgent|immediate|danger|unsafe|hazard)\b", desc) or "ప్రమాద" in raw:
        human_review = True
        return Decimal("0.78"), PriorityLevel.high, human_review
    if re.search(r"\b(blocked|overflow|no water|no power)\b", desc):
        return Decimal("0.55"), PriorityLevel.medium, False
    if re.search(r"\b(but|however|although)\b.+\b(but|however)\b", desc):
        human_review = True
    return Decimal("0.25"), PriorityLevel.low, human_review


def summarize(description: str, max_len: int = 280) -> str:
    text = re.sub(r"\s+", " ", description.strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def analyze_complaint(
    description: str,
    location_text: str,
    ward_or_locality: str | None = None,
    language: str = "en",
) -> AnalysisResult:
    missing = check_completeness(description, location_text, ward_or_locality, language)
    follow_ups = generate_follow_up_questions(missing, language)
    category, cat_confidence = match_category(description, language)
    urgency_score, urgency_label, urgent_review = assess_urgency(description, language)

    confidence = cat_confidence
    if missing:
        confidence = min(confidence, Decimal("0.55"))
    requires_review = urgent_review or bool(missing) or confidence < Decimal("0.5")

    explanation_parts = [
        "Heuristic rules output — not a calibrated probability or ML model score.",
    ]
    if language != "en":
        explanation_parts.append(f"Detected language path: {language}. Full translation service may be unavailable.")
    if category:
        explanation_parts.append(
            f"Keyword rules suggest category '{category.name}' (code {category.code}) with heuristic confidence {cat_confidence}."
        )
    else:
        explanation_parts.append("No strong category keyword match; manual classification recommended.")
    if missing:
        explanation_parts.append(f"Missing information detected: {', '.join(missing)}.")
    if urgent_review:
        explanation_parts.append(
            "Potentially urgent language detected — flagged for human review (not an emergency alert)."
        )

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
            "detected_language": language,
        },
    )
