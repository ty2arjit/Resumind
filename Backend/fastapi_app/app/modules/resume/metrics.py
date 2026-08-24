"""Deterministic metric detection (spec §13). Preserves the original
representation — no judgment about whether a number is "impressive"."""

import re

_METRIC_PATTERNS = [
    r"\d+(?:\.\d+)?\s*%",  # 35%
    r"[₹$€£]\s?\d[\d,]*(?:\.\d+)?\s*(?:lakh|crore|k|m|million|billion)?",  # ₹5 lakh, $10,000
    r"\d+(?:\.\d+)?\s*[xX]\b",  # 3x
    r"\d+(?:\.\d+)?\s?(?:k|K|m|M)\+?\s*(?:users|requests|records|downloads|rows|events)?",  # 10K users
    r"\d+\+\s*(?:projects|users|clients|students|members|issues|repositories|repos)?",  # 50+ projects
    r"\d+(?:\.\d+)?\s*(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?)\b",  # 2 seconds, 40 hours
]
_METRIC_RE = re.compile("|".join(f"(?:{p})" for p in _METRIC_PATTERNS), re.IGNORECASE)


def extract_metrics(text: str) -> list[str]:
    seen: list[str] = []
    for match in _METRIC_RE.finditer(text):
        value = match.group(0).strip()
        if value and value not in seen:
            seen.append(value)
    return seen
