from app.modules.evidence.aggregation import aggregate_evidence_strength, evidence_diversity
from app.modules.evidence.schemas import (
    EvidenceQualitySignals,
    EvidenceSourceType,
    EvidenceStrength,
    RankedEvidence,
)


def _ranked(id, relevance, section=EvidenceSourceType.EXPERIENCE_BULLET):
    return RankedEvidence(
        evidence_id=id,
        text="x",
        section=section,
        strength=EvidenceStrength.STRONG,
        signals=EvidenceQualitySignals(relevance=relevance),
    )


def test_single_strong_evidence_counts_fully():
    result = aggregate_evidence_strength([_ranked("ev_1", 0.9)])
    assert result == 0.9


def test_diminishing_returns_not_linear_multiplication():
    """spec §17: three identical strong mentions must not produce 3x."""
    one = aggregate_evidence_strength([_ranked("ev_1", 0.9)])
    three = aggregate_evidence_strength([_ranked("ev_1", 0.9), _ranked("ev_2", 0.9), _ranked("ev_3", 0.9)])
    assert three > one  # more evidence still helps...
    assert three < one * 3  # ...but nowhere near linearly


def test_empty_evidence_aggregates_to_zero():
    assert aggregate_evidence_strength([]) == 0.0


def test_result_is_bounded():
    many = [_ranked(f"ev_{i}", 1.0) for i in range(10)]
    assert 0.0 <= aggregate_evidence_strength(many) <= 1.0


def test_diversity_rewards_distinct_sections():
    diverse = [
        _ranked("ev_1", 0.8, EvidenceSourceType.EXPERIENCE_BULLET),
        _ranked("ev_2", 0.8, EvidenceSourceType.PROJECT_BULLET),
    ]
    homogeneous = [
        _ranked("ev_1", 0.8, EvidenceSourceType.SKILLS_SECTION),
        _ranked("ev_2", 0.8, EvidenceSourceType.SKILLS_SECTION),
    ]
    assert evidence_diversity(diverse) > evidence_diversity(homogeneous)


def test_diversity_empty_is_zero():
    assert evidence_diversity([]) == 0.0
