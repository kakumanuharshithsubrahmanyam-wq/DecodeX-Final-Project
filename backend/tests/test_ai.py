from decimal import Decimal

from app.ai.rules_engine import analyze_complaint, check_completeness
from app.models.enums import PriorityLevel


def test_vague_description_triggers_missing_fields():
    missing = check_completeness("There is garbage", "Main road", None)
    assert "detailed_description" in missing or "duration_or_timeline" in missing


def test_clear_water_complaint_category():
    desc = (
        "Drinking water supply stopped in Ward 12 near Gandhi Nagar for the past three days. "
        "Multiple households affected."
    )
    result = analyze_complaint(desc, "Gandhi Nagar, Ward 12", "Ward 12")
    assert result.suggested_category_code == "WATER"
    assert result.suggested_department_code == "WATER"
    assert result.confidence >= Decimal("0.45")


def test_urgent_language_flags_review():
    result = analyze_complaint(
        "Live wire sparking on the street near school since yesterday morning, very dangerous for children.",
        "School road, Secunderabad",
        "Secunderabad",
    )
    assert result.urgency_label == PriorityLevel.critical
    assert result.requires_human_review is True


def test_overlapping_sanitation_keywords():
    result = analyze_complaint(
        "Garbage dump and sewage overflow blocking the road near market for two weeks.",
        "Market area, road 5",
        None,
    )
    assert result.suggested_category_code in {"SANITATION", "ROADS", "WATER"}
