"""Deterministic date extraction and normalization (spec §15-16).

Only formats we can parse with high confidence are normalized; anything
ambiguous keeps normalized_date/start_normalized/end_normalized as None
rather than guessing (spec: "Do not invent dates").
"""

import re

from app.modules.resume.schemas import DateRange

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_NAMES = "|".join(sorted(_MONTHS.keys(), key=len, reverse=True))

_CURRENT_WORDS = {"present", "current", "ongoing", "now", "till date", "to date"}

# "Jan 2024", "January 2024"
_MONTH_YEAR_RE = re.compile(rf"\b({_MONTH_NAMES})\.?\s+(\d{{4}})\b", re.IGNORECASE)
# "01/2024" or "1/2024"
_NUMERIC_MONTH_YEAR_RE = re.compile(r"\b(0?[1-9]|1[0-2])[/-](\d{4})\b")
# bare "2024"
_YEAR_ONLY_RE = re.compile(r"\b(19|20)\d{2}\b")

_RANGE_SEPARATOR_RE = re.compile(r"\s*(?:-|–|—|to)\s*", re.IGNORECASE)


def _parse_single_date(text: str) -> tuple[str | None, str]:
    """Returns (normalized "YYYY-MM" or "YYYY" or None, original matched text)."""
    text = text.strip()
    lower = text.lower()
    if lower in _CURRENT_WORDS:
        return None, text

    match = _MONTH_YEAR_RE.search(text)
    if match:
        month = _MONTHS[match.group(1).lower()]
        year = match.group(2)
        return f"{year}-{month:02d}", match.group(0)

    match = _NUMERIC_MONTH_YEAR_RE.search(text)
    if match:
        month, year = int(match.group(1)), match.group(2)
        return f"{year}-{month:02d}", match.group(0)

    match = _YEAR_ONLY_RE.search(text)
    if match:
        return match.group(0), match.group(0)

    return None, text


def _months_between(start: str, end: str) -> int | None:
    """start/end are "YYYY-MM" or "YYYY". Returns whole months, or None if
    either side is year-only (too imprecise to report a month count)."""
    def parts(value: str) -> tuple[int, int] | None:
        if "-" in value:
            y, m = value.split("-")
            return int(y), int(m)
        return None

    start_parts = parts(start)
    end_parts = parts(end)
    if not start_parts or not end_parts:
        return None
    return (end_parts[0] - start_parts[0]) * 12 + (end_parts[1] - start_parts[1])


def _is_within_any(span: tuple[int, int], other_spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start >= s and end <= e for s, e in other_spans)


def extract_date_range(text: str) -> DateRange | None:
    """Finds a date or a date range within free text. Returns None if no
    recognizable date token is present at all."""
    all_month_year = list(_MONTH_YEAR_RE.finditer(text))
    all_numeric = list(_NUMERIC_MONTH_YEAR_RE.finditer(text))
    precise_spans = [m.span() for m in (all_month_year + all_numeric)]

    # A bare "2024" inside "Jan 2024" would otherwise also match
    # _YEAR_ONLY_RE as its own token, double-counting the same date —
    # only keep year-only matches that aren't already covered by a more
    # precise month+year match.
    all_year = [m for m in _YEAR_ONLY_RE.finditer(text) if not _is_within_any(m.span(), precise_spans)]
    has_current_word = any(word in text.lower() for word in _CURRENT_WORDS)

    tokens = sorted(all_month_year + all_numeric + all_year, key=lambda m: m.start())
    if not tokens and not has_current_word:
        return None

    if not tokens and has_current_word:
        return None  # a lone "Present" with no start date isn't a usable range

    start_norm, start_text = _parse_single_date(tokens[0].group(0))

    if len(tokens) >= 2:
        end_norm, end_text = _parse_single_date(tokens[-1].group(0))
        is_current = False
    elif has_current_word:
        end_norm, end_text, is_current = None, "Present", True
    else:
        end_norm, end_text, is_current = None, None, False

    duration = None
    if start_norm and end_norm:
        duration = _months_between(start_norm, end_norm)
    elif start_norm and is_current:
        from datetime import date

        now = date.today()
        duration = _months_between(start_norm, f"{now.year}-{now.month:02d}")

    return DateRange(
        start_text=start_text,
        end_text=end_text,
        start_normalized=start_norm,
        end_normalized=end_norm,
        is_current=is_current,
        duration_months=duration,
    )
