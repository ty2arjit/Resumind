"""Evidence context signal (spec §15) — a provisional, centrally
configured strength-by-section signal, not a final weighting decision."""

from app.modules.matching.schemas import MatchableEvidence
from app.modules.scoring.config import get_scoring_config


def context_signal(evidence: MatchableEvidence) -> float:
    weights = get_scoring_config().evidence_context_weights
    return weights.for_context(evidence.context.value)
