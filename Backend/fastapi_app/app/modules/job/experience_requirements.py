"""Explicit experience-requirement extraction (spec §10).

Only fires on genuinely explicit "N years" phrasing — never infers a
requirement from unrelated context (spec: "Do not infer experience
requirements when the JD does not explicitly state them").
"""

import re

from app.modules.job.schemas import ExperienceRequirement

# "3-5 years", "3 to 5 years"
_RANGE_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\+?\s*years?\b", re.IGNORECASE)
# "2+ years"
_PLUS_RE = re.compile(r"\b(\d+(?:\.\d+)?)\+\s*years?\b", re.IGNORECASE)
# "at least 1 year", "minimum of 2 years", "minimum 2 years"
_AT_LEAST_RE = re.compile(
    r"\b(?:at least|minimum(?: of)?)\s+(\d+(?:\.\d+)?)\s*years?\b", re.IGNORECASE
)
# plain "3 years" / "3 years of experience" with no qualifier at all
_PLAIN_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*years?\b", re.IGNORECASE)

_LEADING_CONNECTOR_RE = re.compile(r"^(?:of experience\s+)?(?:in|with|as|of)\s+", re.IGNORECASE)


def _extract_context(text: str, match_end: int) -> str | None:
    """The technology/role phrase the years qualify, e.g. "years of Python
    development" -> "Python development". Falls back to None rather than
    guessing when nothing follows."""
    tail = text[match_end:].strip(" .,;")
    # Stop at the next clause boundary.
    tail = re.split(r"[.;\n]| and | or ", tail, maxsplit=1)[0].strip()
    tail = _LEADING_CONNECTOR_RE.sub("", tail).strip()
    return tail or None


def extract_experience_requirement(text: str) -> ExperienceRequirement | None:
    """Finds one explicit experience-years phrase in `text`. Returns None
    if none is present — this is a detector, not a guesser."""
    match = _RANGE_RE.search(text)
    if match:
        context = _extract_context(text, match.end())
        return ExperienceRequirement(
            min_years=float(match.group(1)), max_years=float(match.group(2)), context=context, raw_text=match.group(0)
        )

    match = _PLUS_RE.search(text)
    if match:
        context = _extract_context(text, match.end())
        return ExperienceRequirement(min_years=float(match.group(1)), max_years=None, context=context, raw_text=match.group(0))

    match = _AT_LEAST_RE.search(text)
    if match:
        context = _extract_context(text, match.end())
        return ExperienceRequirement(min_years=float(match.group(1)), max_years=None, context=context, raw_text=match.group(0))

    match = _PLAIN_RE.search(text)
    if match:
        context = _extract_context(text, match.end())
        return ExperienceRequirement(min_years=float(match.group(1)), max_years=float(match.group(1)), context=context, raw_text=match.group(0))

    return None
