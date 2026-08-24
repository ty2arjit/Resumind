"""Responsibility matching (spec §17). Separate action/object/technology/
semantic signals — never combined into a final score here."""

from app.modules.matching.keyword import keyword_signal
from app.modules.matching.schemas import MatchableEvidence, ResponsibilityMatchSignals
from app.modules.normalization import NormalizationService
from app.modules.resume.actions import leading_action

_service = NormalizationService()


def _action_signal(requirement_text: str, evidence: MatchableEvidence) -> float:
    """Uses Phase 4's normalized action vocabulary (spec §11) — the
    requirement's and evidence's leading verbs must map to the same
    canonical action to count as a match; not every verb pair is treated
    as equivalent."""
    requirement_action = leading_action(requirement_text)
    if requirement_action is None or not evidence.actions:
        return 0.0

    requirement_canonical = _service.normalize_action(requirement_action).canonical_action
    if requirement_canonical is None:
        return 0.0

    for action in evidence.actions:
        if _service.normalize_action(action).canonical_action == requirement_canonical:
            return 1.0
    return 0.0


def _object_signal(requirement_text: str, evidence: MatchableEvidence) -> float:
    """Lightweight lexical proxy for object similarity (spec §12) — full
    semantic object matching is the semantic signal's job; this is the
    deterministic keyword-overlap component of it."""
    signal, _ = keyword_signal(requirement_text, evidence.text)
    return signal


def _technology_signal(requirement_text: str, evidence: MatchableEvidence) -> float:
    from app.modules.matching.canonical import canonical_signal
    from app.modules.resume.technologies import extract_technologies

    requirement_technologies = extract_technologies(requirement_text)
    if not requirement_technologies:
        return 0.0
    signal, _ = canonical_signal(requirement_technologies, evidence)
    return signal


def match_responsibility(
    requirement_text: str, evidence: MatchableEvidence, semantic_signal: float | None
) -> ResponsibilityMatchSignals:
    return ResponsibilityMatchSignals(
        action_signal=_action_signal(requirement_text, evidence),
        object_signal=_object_signal(requirement_text, evidence),
        technology_signal=_technology_signal(requirement_text, evidence),
        semantic_signal=semantic_signal,
    )
