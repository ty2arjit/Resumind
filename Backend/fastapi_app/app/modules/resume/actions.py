"""Lightweight deterministic action-verb detection (spec §12).

Not semantic role labeling — just a vocabulary lookup. The vocabulary
lives in data/action_verbs.json (see vocab.py) so it can be extended
without touching this logic.
"""

import re

from app.modules.resume.vocab import get_action_verbs


def _build_pattern() -> re.Pattern:
    escaped = [re.escape(verb) for verb in get_action_verbs()]
    return re.compile(r"\b(?:" + "|".join(escaped) + r")\b", re.IGNORECASE)


_ACTION_PATTERN = _build_pattern()


def extract_actions(text: str) -> list[str]:
    """Returns matched action verbs in their original casing, in order of
    appearance, deduplicated. The leading verb (index 0, if present) is
    the bullet's primary action."""
    seen: list[str] = []
    for match in _ACTION_PATTERN.finditer(text):
        value = match.group(0)
        if value not in seen:
            seen.append(value)
    return seen


def leading_action(text: str) -> str | None:
    """The action verb only if it's (close to) the first word of the
    bullet — used by evidence.py to anchor object-phrase extraction."""
    stripped = text.strip()
    match = _ACTION_PATTERN.match(stripped)
    if match:
        return match.group(0)
    return None
