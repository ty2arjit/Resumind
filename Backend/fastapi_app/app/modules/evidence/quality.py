"""Builds EvidenceQualitySignals (spec §10-14) from a Phase 5
HybridMatchResult plus responsibility signals and metric detection —
reuses Phase 5's matching outputs rather than recomputing relevance.
"""

from app.modules.evidence.schemas import EvidenceItem, EvidenceQualitySignals
from app.modules.matching.responsibility import match_responsibility
from app.modules.matching.schemas import HybridMatchResult, MatchableEvidence


def build_quality_signals(
    requirement_text: str, match_result: HybridMatchResult, evidence: EvidenceItem, matchable: MatchableEvidence
) -> EvidenceQualitySignals:
    responsibility = match_responsibility(requirement_text, matchable, match_result.signals.semantic)

    return EvidenceQualitySignals(
        relevance=match_result.score,
        semantic_similarity=match_result.signals.semantic,
        lexical_relevance=match_result.signals.keyword,
        canonical_entity_match=1.0 if match_result.explanation.canonical_entity_match else 0.0,
        context_strength=match_result.signals.context,
        action_match=responsibility.action_signal if evidence.actions else None,
        object_match=responsibility.object_signal,
        technology_match=responsibility.technology_signal if evidence.technologies else None,
        metric_presence=1.0 if evidence.metrics else 0.0,
    )
