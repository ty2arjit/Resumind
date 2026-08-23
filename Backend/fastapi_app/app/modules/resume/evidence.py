"""Bullet -> structured Evidence (spec §11).

This is NOT requirement matching (spec §20) — it only records what a
bullet contains. "objects" extraction is intentionally a simple heuristic
(phrase between the leading action verb and the next preposition/comma),
not full parsing — good enough to be useful and explainable, not claimed
to be linguistically precise.
"""

import re

from app.modules.resume.actions import extract_actions, leading_action
from app.modules.resume.metrics import extract_metrics
from app.modules.resume.schemas import CanonicalSection, Evidence
from app.modules.resume.technologies import extract_technologies

_PREPOSITION_SPLIT_RE = re.compile(
    r"\s+(?:using|via|with|for|by|to|in|on|through|across)\s+|,", re.IGNORECASE
)
_IMPACT_CLAUSE_RE = re.compile(
    r"\b(?:reduc\w*|increas\w*|improv\w*|decreas\w*|boost\w*|cut\w*)\s+(.+?)\s+by\s",
    re.IGNORECASE,
)


def _extract_objects(text: str, primary_action: str | None) -> list[str]:
    objects: list[str] = []

    if primary_action:
        after_action = text[text.lower().find(primary_action.lower()) + len(primary_action):]
        first_chunk = _PREPOSITION_SPLIT_RE.split(after_action, maxsplit=1)[0].strip(" .,")
        if first_chunk:
            objects.append(first_chunk)

    impact_match = _IMPACT_CLAUSE_RE.search(text)
    if impact_match:
        phrase = impact_match.group(1).strip(" .,")
        if phrase and phrase not in objects:
            objects.append(phrase)

    return objects


def build_evidence(text: str, section: CanonicalSection, position: str | None = None) -> Evidence:
    primary_action = leading_action(text)
    return Evidence(
        text=text.strip(),
        section=section,
        position=position,
        actions=extract_actions(text),
        technologies=extract_technologies(text),
        metrics=extract_metrics(text),
        objects=_extract_objects(text, primary_action),
    )
