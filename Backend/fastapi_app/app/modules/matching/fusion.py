"""Hybrid signal fusion (spec §21-23).

Combines the raw per-technique signals into ONE preliminary match
strength per requirement-evidence pair — explicitly NOT the final ATS
score (that's Phase 7, using different weights entirely: see
SignalFusionWeights vs RequirementSignalWeights in scoring/config.py).
"""

from app.models.enums import MatchStrength
from app.modules.matching.schemas import MatchSignals
from app.modules.scoring.config import get_scoring_config

_SIGNAL_NAMES = ("exact", "canonical", "keyword", "tfidf", "semantic", "context")


def fuse_signals(signals: MatchSignals) -> tuple[float, float]:
    """Returns (fused_score, confidence). confidence reflects how much of
    the configured weight was actually backed by a computed signal — if
    the semantic signal is unavailable, its weight is excluded from the
    denominator rather than silently counted as 0, so a missing signal
    lowers confidence without unfairly penalizing the score.
    """
    weights = get_scoring_config().signal_fusion_weights
    weight_map = weights.model_dump()
    signal_map = signals.model_dump()

    active_weight_total = 0.0
    weighted_sum = 0.0
    for name in _SIGNAL_NAMES:
        value = signal_map[name]
        if value is None:
            continue
        weight = weight_map[name]
        weighted_sum += weight * value
        active_weight_total += weight

    if active_weight_total == 0:
        return 0.0, 0.0

    fused_score = weighted_sum / active_weight_total
    confidence = active_weight_total  # weights already sum to 1.0 when fully available

    # Entity identity confirmed by a deterministic technique (exact string
    # match, or Phase 4's canonical resolution) is a floor, not just
    # another additively-weighted term: a resume that says "Postgres"
    # against a "PostgreSQL" requirement has *confirmed* the right
    # technology even though the differently-spelled evidence text
    # legitimately scores 0 on keyword/TF-IDF. Pure linear averaging would
    # otherwise let wording differences understate a confirmed match. This
    # never fabricates STRONG/VERY_STRONG on its own — it only guarantees
    # PARTIAL; reaching higher still requires real signal support.
    if signal_map["exact"] == 1.0 or signal_map["canonical"] == 1.0:
        fused_score = max(fused_score, get_scoring_config().match_strength_thresholds.partial)

    return fused_score, confidence


def classify_match_strength(fused_score: float) -> MatchStrength:
    thresholds = get_scoring_config().match_strength_thresholds
    if fused_score >= thresholds.very_strong:
        return MatchStrength.VERY_STRONG
    if fused_score >= thresholds.strong:
        return MatchStrength.STRONG
    if fused_score >= thresholds.partial:
        return MatchStrength.PARTIAL
    if fused_score >= thresholds.weak:
        return MatchStrength.WEAK
    return MatchStrength.MISSING
