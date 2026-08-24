from app.models.enums import ImportanceLevel, MatchStrength, RequirementType
from app.modules.evidence.schemas import (
    EvidenceQualitySignals,
    EvidenceSourceType,
    EvidenceStrength,
    ExperienceEvidence,
    QualificationEvidence,
    RankedEvidence,
    RequirementEvidenceResult,
)
from app.modules.job.schemas import LogicalOperator, Requirement
from app.modules.scoring.requirement_scoring import score_requirement


def _requirement(
    id="req_1", text="Python", req_type=RequirementType.SKILL, importance=ImportanceLevel.REQUIRED,
    weight=1.0, critical=False, technologies=None, operator=None, experience=None,
):
    return Requirement(
        id=id, text=text, type=req_type, importance=importance, weight=weight, critical=critical,
        confidence=0.9, technologies=technologies or [], operator=operator, experience=experience,
    )


def _evidence_result(match_result, relevance=0.8, evidence_present=True):
    evidence = (
        [
            RankedEvidence(
                evidence_id="ev_1", text="x", section=EvidenceSourceType.EXPERIENCE_BULLET,
                strength=EvidenceStrength.STRONG,
                signals=EvidenceQualitySignals(relevance=relevance, lexical_relevance=0.7, semantic_similarity=0.6, context_strength=0.95),
            )
        ]
        if evidence_present
        else []
    )
    return RequirementEvidenceResult(
        requirement_id="req_1", match_result=match_result, evidence=evidence, aggregated_evidence_strength=relevance
    )


# --- basic status/score consistency (spec §12) ---

def test_missing_status_produces_near_zero_score():
    result = score_requirement(_requirement(), _evidence_result(MatchStrength.MISSING, relevance=0.1), set())
    assert result.status == "MISSING"
    assert result.score < 0.15


def test_very_strong_status_produces_high_score():
    result = score_requirement(_requirement(), _evidence_result(MatchStrength.VERY_STRONG, relevance=0.95), set())
    assert result.status == "VERY_STRONG"
    assert result.score > 0.85


def test_no_evidence_at_all_scores_at_missing_anchor():
    result = score_requirement(_requirement(), _evidence_result(MatchStrength.MISSING, evidence_present=False), set())
    assert result.score == 0.0
    assert result.evidence_text is None
    assert result.evidence_source is None


def test_top_evidence_is_passed_through_for_display():
    result = score_requirement(_requirement(), _evidence_result(MatchStrength.STRONG, relevance=0.9), set())
    assert result.evidence_text == "x"
    assert result.evidence_source == "Experience"


# --- UNKNOWN handling (spec §10) ---

def test_unknown_match_result_is_not_zero():
    """UNKNOWN must never be silently treated as MISSING (score 0)."""
    result = score_requirement(_requirement(), _evidence_result(MatchStrength.UNKNOWN), set())
    assert result.status == "UNKNOWN"
    assert 0.0 < result.score < 1.0


# --- critical requirement (spec §9, §18) ---

def test_critical_penalty_is_off_by_default():
    """spec §9: must not create an absurd system where a missing
    requirement automatically zeroes the score unless explicitly enabled."""
    normal = score_requirement(_requirement(critical=False), _evidence_result(MatchStrength.MISSING, relevance=0.1), set())
    critical = score_requirement(_requirement(critical=True), _evidence_result(MatchStrength.MISSING, relevance=0.1), set())
    assert normal.score == critical.score  # penalty disabled by default -> no difference
    assert critical.critical is True


# --- experience requirements (spec §21) ---

def test_experience_full_ratio_is_very_strong():
    req = _requirement(req_type=RequirementType.EXPERIENCE)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        experience=ExperienceEvidence(required_years=3.0, detected_relevant_years=3.5, date_confidence=0.9),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "VERY_STRONG"


def test_experience_partial_ratio_is_partial():
    req = _requirement(req_type=RequirementType.EXPERIENCE)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        experience=ExperienceEvidence(required_years=3.0, detected_relevant_years=2.2, date_confidence=0.9),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "PARTIAL"


def test_experience_unreliable_dates_is_unknown_not_missing():
    req = _requirement(req_type=RequirementType.EXPERIENCE)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        experience=ExperienceEvidence(required_years=3.0, detected_relevant_years=None, date_confidence=0.3),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "UNKNOWN"


def test_experience_confidently_absent_is_missing():
    req = _requirement(req_type=RequirementType.EXPERIENCE)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        experience=ExperienceEvidence(required_years=3.0, detected_relevant_years=None, date_confidence=0.9),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "MISSING"


# --- qualification requirements (spec §22) ---

def test_qualification_confident_match_is_very_strong():
    req = _requirement(req_type=RequirementType.QUALIFICATION)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        qualification=QualificationEvidence(degree="B.Tech", field="Computer Science", matched=True, uncertain=False),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "VERY_STRONG"


def test_qualification_no_education_evidence_is_unknown():
    req = _requirement(req_type=RequirementType.QUALIFICATION)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        qualification=QualificationEvidence(matched=False, uncertain=True),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "UNKNOWN"


def test_qualification_unrelated_degree_is_missing():
    req = _requirement(req_type=RequirementType.QUALIFICATION)
    evidence_result = RequirementEvidenceResult(
        requirement_id="req_1", match_result=MatchStrength.UNKNOWN,
        qualification=QualificationEvidence(degree="B.Tech", field="Biotechnology", matched=False, uncertain=True),
    )
    result = score_requirement(req, evidence_result, set())
    assert result.status == "MISSING"


# --- AND requirements (spec §23) ---

def test_and_requirement_full_coverage_is_unpenalized():
    req = _requirement(technologies=["Python", "FastAPI"], operator=LogicalOperator.AND)
    result = score_requirement(req, _evidence_result(MatchStrength.STRONG, relevance=0.9), {"Python", "FastAPI"})
    assert result.score > 0.7


def test_and_requirement_partial_coverage_is_reduced():
    req = _requirement(technologies=["Python", "FastAPI"], operator=LogicalOperator.AND)
    full = score_requirement(req, _evidence_result(MatchStrength.STRONG, relevance=0.9), {"Python", "FastAPI"})
    partial = score_requirement(req, _evidence_result(MatchStrength.STRONG, relevance=0.9), {"Python"})
    assert partial.score < full.score


def test_or_requirement_is_not_penalized_for_partial_technology_set():
    """OR semantics come for free from Phase 5/6's set-membership matching
    — no AND-coverage adjustment should apply."""
    req = _requirement(technologies=["Python", "Java"], operator=LogicalOperator.OR)
    result = score_requirement(req, _evidence_result(MatchStrength.STRONG, relevance=0.9), {"Python"})
    unadjusted = score_requirement(_requirement(technologies=[], operator=None), _evidence_result(MatchStrength.STRONG, relevance=0.9), set())
    assert result.score == unadjusted.score


# --- bounds ---

def test_score_is_always_bounded():
    for match_result in MatchStrength:
        if match_result == MatchStrength.UNKNOWN:
            continue
        result = score_requirement(_requirement(), _evidence_result(match_result), set())
        assert 0.0 <= result.score <= 1.0


def test_determinism():
    req = _requirement()
    evidence_result = _evidence_result(MatchStrength.STRONG, relevance=0.8)
    results = [score_requirement(req, evidence_result, set()) for _ in range(3)]
    assert len({r.score for r in results}) == 1
