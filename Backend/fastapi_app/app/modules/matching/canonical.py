"""Canonical/normalized matching (spec §5-6).

All canonicalization comes from Phase 4's NormalizationService — this
module must never maintain its own alias table. Distinct-entity
protection (Docker != Kubernetes) falls out of that naturally: Phase 4
only ever resolves genuine aliases to the same canonical value.
"""

from app.modules.matching.schemas import MatchableEvidence
from app.modules.normalization import NormalizationService

_service = NormalizationService()


def canonical_signal(requirement_technologies: list[str], evidence: MatchableEvidence) -> tuple[float | None, str | None]:
    """Returns (signal, matched_canonical_value). signal is None when the
    requirement has no resolvable canonical technology — "not
    applicable", distinct from 0.0 ("applicable, no match")."""
    if not requirement_technologies:
        return None, None

    requirement_canonicals = {
        result.canonical_value
        for result in (_service.normalize_skill(t) for t in requirement_technologies)
        if result.canonical_value is not None
    }
    if not requirement_canonicals:
        return None, None

    for tech in evidence.technologies:
        canonical = _service.normalize_skill(tech).canonical_value
        if canonical is not None and canonical in requirement_canonicals:
            return 1.0, canonical

    return 0.0, None


def is_known_technology_mismatch(requirement_technologies: list[str], evidence: MatchableEvidence) -> bool:
    """spec §6/§16 — a HARD guardrail, not just favorable weighting: when
    the evidence explicitly names a *different*, specifically-known
    technology than the one required (Docker evidence for a Kubernetes
    requirement), that must never be rescued into a strong match by a
    merely-high semantic score. Returns False (no guardrail trip) when
    either side has no resolvable canonical technology to compare —
    absence of evidence is not the same as contradicting evidence.
    """
    requirement_canonicals = {
        result.canonical_value
        for result in (_service.normalize_skill(t) for t in requirement_technologies)
        if result.canonical_value is not None
    }
    if not requirement_canonicals:
        return False

    evidence_canonicals = {
        result.canonical_value
        for result in (_service.normalize_skill(t) for t in evidence.technologies)
        if result.canonical_value is not None
    }
    if not evidence_canonicals:
        return False

    return requirement_canonicals.isdisjoint(evidence_canonicals)
