"""Evidence aggregation with diminishing returns and diversity (spec
§17-19). Three identical strong mentions must not produce 3x the
evidence strength of one.
"""

from app.modules.evidence.schemas import RankedEvidence
from app.modules.scoring.config import get_scoring_config


def aggregate_evidence_strength(ranked_evidence: list[RankedEvidence]) -> float:
    """Strongest item counts fully; each additional item contributes a
    shrinking bonus (spec §17) rather than being averaged or summed
    linearly. Ranked_evidence is expected already sorted strongest-first
    (retrieve_candidates guarantees this)."""
    if not ranked_evidence:
        return 0.0

    weights = get_scoring_config().evidence_aggregation.diminishing_weights
    total = 0.0
    for i, item in enumerate(ranked_evidence):
        weight = weights[i] if i < len(weights) else weights[-1] * 0.5
        total += weight * item.signals.relevance

    return max(0.0, min(1.0, total))


def evidence_diversity(ranked_evidence: list[RankedEvidence]) -> float:
    """spec §19 — fraction of the selected evidence's sections that are
    distinct. Experience + Project scores higher than Skills + Skills +
    Skills of the same size."""
    if not ranked_evidence:
        return 0.0
    distinct_sections = len({item.section for item in ranked_evidence})
    return distinct_sections / len(ranked_evidence)
