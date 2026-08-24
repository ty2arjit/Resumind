"""Evidence deduplication (spec §9). Detects exact and near-duplicate
evidence text so repeated/duplicated bullets don't occupy multiple top-K
slots and artificially inflate evidence strength.
"""

import re

from app.modules.evidence.schemas import EvidenceItem

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", _PUNCT_RE.sub("", text.lower())).strip()


def deduplicate(items: list[EvidenceItem]) -> tuple[list[EvidenceItem], list[str]]:
    """Returns (deduplicated_items, warnings). Keeps the first occurrence
    of each normalized text; later exact/near-duplicates are dropped."""
    result: list[EvidenceItem] = []
    seen_by_key: dict[str, EvidenceItem] = {}
    warnings: list[str] = []

    for item in items:
        key = _normalize(item.text)
        if not key:
            result.append(item)  # never drop on an empty key
            continue
        existing = seen_by_key.get(key)
        if existing is not None:
            warnings.append(f"Duplicate evidence text detected and suppressed: {item.text!r} (kept {existing.id})")
            continue
        seen_by_key[key] = item
        result.append(item)

    return result, warnings
