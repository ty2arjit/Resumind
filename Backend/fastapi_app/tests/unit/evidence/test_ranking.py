from app.modules.evidence.ranking import rank_by_evidence_hierarchy
from app.modules.evidence.schemas import (
    EvidenceQualitySignals,
    EvidenceSourceType,
    EvidenceStrength,
    RankedEvidence,
)


def _ranked(id, relevance, context_strength, section):
    return RankedEvidence(
        evidence_id=id,
        text="x",
        section=section,
        strength=EvidenceStrength.STRONG,
        signals=EvidenceQualitySignals(relevance=relevance, context_strength=context_strength),
    )


def test_experience_evidence_outranks_a_slightly_higher_relevance_skills_mention():
    """spec §5: a bare skills-section mention scoring marginally higher on
    raw relevance must not outrank a rich experience bullet."""
    skills = _ranked("ev_skill", relevance=0.88, context_strength=0.55, section=EvidenceSourceType.SKILLS_SECTION)
    experience = _ranked("ev_exp", relevance=0.81, context_strength=0.95, section=EvidenceSourceType.EXPERIENCE_BULLET)

    ranked = rank_by_evidence_hierarchy([skills, experience])
    assert ranked[0].evidence_id == "ev_exp"


def test_large_relevance_gap_still_wins_on_relevance():
    """The hierarchy correction shouldn't invert an obviously stronger
    match just because of section — it only corrects close calls."""
    skills = _ranked("ev_skill", relevance=0.95, context_strength=0.55, section=EvidenceSourceType.SKILLS_SECTION)
    experience = _ranked("ev_exp", relevance=0.20, context_strength=0.95, section=EvidenceSourceType.EXPERIENCE_BULLET)

    ranked = rank_by_evidence_hierarchy([skills, experience])
    assert ranked[0].evidence_id == "ev_skill"


def test_does_not_mutate_relevance():
    skills = _ranked("ev_skill", relevance=0.88, context_strength=0.55, section=EvidenceSourceType.SKILLS_SECTION)
    ranked = rank_by_evidence_hierarchy([skills])
    assert ranked[0].signals.relevance == 0.88
