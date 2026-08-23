"""Raw technology/entity mention detection (spec §14).

Deliberately does NOT normalize "React.js" / "ReactJS" / "React" to a
single canonical form — that's Phase 4's job. This module only detects
that a known technology term appears, and returns the exact substring as
it appears in the source text.
"""

import re

from app.modules.resume.vocab import get_technology_keywords


def _build_pattern() -> re.Pattern:
    # Longest terms first so "React.js" matches before the shorter "React"
    # inside it would otherwise steal the match.
    terms = sorted(get_technology_keywords(), key=len, reverse=True)
    escaped = [re.escape(term) for term in terms]
    pattern = r"(?<![\w.])(?:" + "|".join(escaped) + r")(?![\w])"
    return re.compile(pattern, re.IGNORECASE)


_TECH_PATTERN = _build_pattern()


def extract_technologies(text: str) -> list[str]:
    seen: list[str] = []
    for match in _TECH_PATTERN.finditer(text):
        value = match.group(0)
        if value not in seen:
            seen.append(value)
    return seen
