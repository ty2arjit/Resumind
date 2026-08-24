from app.modules.evidence.schemas import EvidenceStrength
from app.modules.evidence.strength import classify_evidence_strength


def test_thresholds():
    assert classify_evidence_strength(1.0) == EvidenceStrength.VERY_STRONG
    assert classify_evidence_strength(0.90) == EvidenceStrength.STRONG
    assert classify_evidence_strength(0.70) == EvidenceStrength.MODERATE
    assert classify_evidence_strength(0.40) == EvidenceStrength.WEAK
    assert classify_evidence_strength(0.0) == EvidenceStrength.MISSING
