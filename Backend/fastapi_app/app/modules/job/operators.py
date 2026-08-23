"""Logical operator detection (spec §16).

Deliberately narrow: only fires when two or more known technology
mentions are joined by a bare "and"/"or"/comma-or" in the text. Anything
else is left as None and the original text is preserved — no attempt at
general natural-language logic parsing.
"""

import re

from app.modules.job.schemas import LogicalOperator
from app.modules.resume.technologies import extract_technologies

_OR_JOIN_RE = re.compile(r"\bor\b|,\s*or\b", re.IGNORECASE)
_AND_JOIN_RE = re.compile(r"\band\b", re.IGNORECASE)


def detect_operator(text: str) -> LogicalOperator | None:
    technologies = extract_technologies(text)
    if len(technologies) < 2:
        return None

    if _OR_JOIN_RE.search(text):
        return LogicalOperator.OR
    if _AND_JOIN_RE.search(text):
        return LogicalOperator.AND
    return None
