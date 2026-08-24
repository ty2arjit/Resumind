"""Exact matching (spec §4). Deterministic string-identity comparison of
technology mentions — not the final match decision, just one signal."""

from app.modules.matching.schemas import MatchableEvidence


def exact_signal(requirement_technologies: list[str], evidence: MatchableEvidence) -> float | None:
    """None when the requirement names no specific technology at all —
    "not applicable", distinct from 0.0 ("applicable, no match")."""
    if not requirement_technologies:
        return None
    return 1.0 if set(requirement_technologies) & set(evidence.technologies) else 0.0
