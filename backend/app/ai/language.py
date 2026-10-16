from __future__ import annotations

import re

TELUGU_RANGE = re.compile(r"[\u0C00-\u0C7F]")


def detect_language(description: str, location_text: str = "") -> str:
    """Returns en | te | mixed (heuristic, not a calibrated classifier)."""
    text = f"{description} {location_text}"
    telugu_chars = len(TELUGU_RANGE.findall(text))
    latin_words = len(re.findall(r"[A-Za-z]+", text))
    if telugu_chars >= 8 and latin_words >= 3:
        return "mixed"
    if telugu_chars >= 4:
        return "te"
    return "en"


def normalize_text_preserve(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.strip())
