"""Generic deterministic heading-detection engine.

Used by both app.modules.resume.sections and app.modules.job.sections —
the algorithm (dictionary match + conservative structural fallback) is
identical between resumes and job descriptions; only the canonical-type
enum and synonym vocabulary differ per domain, so those stay in each
domain's own module while this file owns the shared mechanics.
"""

import re
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

_MAX_HEADING_WORDS = 6
_MAX_HEADING_CHARS = 60
_TRAILING_PUNCT_RE = re.compile(r"[\s:.\-–—]+$")


@dataclass
class HeadingMatch(Generic[T]):
    line_index: int
    canonical_type: T
    heading_text: str
    confidence: float


def build_synonym_index(section_headings: dict[str, list[str]], canonical_factory) -> dict[str, T]:
    """section_headings: canonical name (str) -> list of synonym strings.
    canonical_factory: converts the canonical name string to the caller's
    enum type."""
    index: dict[str, T] = {}
    for canonical, synonyms in section_headings.items():
        for synonym in synonyms:
            index[synonym.lower()] = canonical_factory(canonical)
    return index


def _normalize_heading_candidate(line: str) -> str:
    return _TRAILING_PUNCT_RE.sub("", line.strip()).lower()


def _looks_like_heading_structurally(line: str) -> bool:
    """Deliberately conservative: this only exists to catch section
    headings outside the synonym dictionary. Anything with a digit, a
    comma, or a pipe is far more likely to be a data/content line ("Role,
    Company", "2020 - 2024", "CGPA: 9.23", "3+ years required", "Project
    Name | React, Node.js") than a section title — a "Name | Tech Stack"
    project header in Title Case would otherwise satisfy Python's
    istitle() (pipes act as word separators) and get misread as a bogus
    section boundary, silently truncating the real section's content.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > _MAX_HEADING_CHARS:
        return False
    if len(stripped.split()) > _MAX_HEADING_WORDS:
        return False
    if stripped.endswith((".", ",", ";")):
        return False
    if "," in stripped or "|" in stripped or any(ch.isdigit() for ch in stripped):
        return False
    # A colon followed by more text is a "Label: Value" line ("Company:
    # Example Corp"), not a heading — a real heading's colon, if any, is
    # trailing and already stripped before this check runs.
    colon_index = stripped.find(":")
    if 0 <= colon_index < len(stripped) - 1:
        return False
    letters_only = "".join(ch for ch in stripped if ch.isalpha())
    if len(letters_only) < 3:
        return False
    is_upper = letters_only.isupper()
    is_title = stripped.istitle()
    return is_upper or is_title


def detect_headings(
    lines: list[str],
    synonym_index: dict[str, T],
    fallback_type: T,
    skip_first_line: bool = False,
) -> list[HeadingMatch]:
    """Finds heading candidates. `fallback_type` is used (at low
    confidence) for structurally heading-like lines outside the synonym
    dictionary — callers that want that OTHER-style bucket pass their own
    enum's fallback member; callers that don't want the structural
    fallback at all can filter it out afterward by confidence.

    skip_first_line: resumes never have a section heading on line 0 (it's
    the candidate's name) — job descriptions don't have that guarantee
    (line 0 is often the job title, but titles aren't headings either in
    practice), so this stays a caller-controlled flag rather than a
    hardcoded assumption.
    """
    matches: list[HeadingMatch] = []

    for i, line in enumerate(lines):
        candidate = _normalize_heading_candidate(line)
        if not candidate:
            continue

        canonical = synonym_index.get(candidate)
        if canonical is not None:
            matches.append(HeadingMatch(i, canonical, line.strip(), 0.95))
            continue

        if skip_first_line and i == 0:
            continue

        if _looks_like_heading_structurally(line):
            matches.append(HeadingMatch(i, fallback_type, line.strip(), 0.4))

    return matches
