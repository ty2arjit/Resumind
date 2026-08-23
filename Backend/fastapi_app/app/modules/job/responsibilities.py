"""Builds the top-level `responsibilities` view (spec §13, §21) from
RESPONSIBILITY-typed requirements — a lightweight action/object split,
not semantic role labeling.
"""

import re

from app.modules.job.schemas import Requirement, Responsibility
from app.modules.resume.actions import leading_action

_PREPOSITION_SPLIT_RE = re.compile(
    r"\s+(?:using|via|with|for|by|to|in|on|through|across)\s+|,", re.IGNORECASE
)


def _extract_object(text: str, action: str | None) -> str | None:
    if action is None:
        return None
    idx = text.lower().find(action.lower())
    if idx == -1:
        return None
    after_action = text[idx + len(action) :]
    first_chunk = _PREPOSITION_SPLIT_RE.split(after_action, maxsplit=1)[0].strip(" .,")
    return first_chunk or None


def build_responsibilities(requirements: list[Requirement]) -> list[Responsibility]:
    responsibilities = []
    for req in requirements:
        if req.type.value != "RESPONSIBILITY":
            continue
        action = leading_action(req.text)
        responsibilities.append(
            Responsibility(
                text=req.text,
                action=action,
                object=_extract_object(req.text, action),
                source_section=req.source_section,
            )
        )
    return responsibilities
