"""Evidence strength classification (spec §16) — independent of Phase 5's
MatchStrength; uses its own thresholds/terminology (MODERATE, not
PARTIAL) even though the initial numeric buckets are the same shape."""

from app.modules.evidence.schemas import EvidenceStrength
from app.modules.scoring.config import get_scoring_config


def classify_evidence_strength(relevance: float) -> EvidenceStrength:
    thresholds = get_scoring_config().evidence_strength_thresholds
    if relevance >= thresholds.very_strong:
        return EvidenceStrength.VERY_STRONG
    if relevance >= thresholds.strong:
        return EvidenceStrength.STRONG
    if relevance >= thresholds.moderate:
        return EvidenceStrength.MODERATE
    if relevance >= thresholds.weak:
        return EvidenceStrength.WEAK
    return EvidenceStrength.MISSING
