from __future__ import annotations

# Transliterated / common Telugu civic keywords (rules fallback only)
TELUGU_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "SANITATION": ["చెత్త", "గార్బేజ్", "drainage", "మురికి", "dump"],
    "ROADS": ["గుంట", "pothole", "రోడ్", "footpath"],
    "WATER": ["నీరు", "water", "tap", "pipeline", "leak"],
    "POWER": ["కరెంట్", "power", "transformer", "wire", "street light"],
    "HEALTH": ["mosquito", "fogging", "clinic", "stray"],
}

TELUGU_URGENT = [" అగ్ని", "fire", "ప్రమాద", "danger", "live wire", "children"]

TELUGU_FOLLOW_UPS: dict[str, tuple[str, str, bool]] = {
    "detailed_description": (
        "desc_detail_te",
        "దయచేసి సమస్యను వివరంగా చెప్పండి — ఏమి జరిగింది, ఎవరికి ఇబ్బంది?",
        True,
    ),
    "location": ("loc_detail_te", "ఖచ్చితమైన స్థలం లేదా ల్యాండ్‌మార్క్ ఇవ్వండి.", True),
    "locality_or_landmark": ("locality_te", "వార్డ్/కాలనీ/ల్యాండ్‌మార్క్ పేరు ఏమిటి?", True),
    "duration_or_timeline": ("duration_te", "ఈ సమస్య ఎంత కాలంగా ఉంది?", False),
}
