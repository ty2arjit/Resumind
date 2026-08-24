"""Unit tests for gap/strength detection and prioritization, built
directly from RequirementScoreResult objects (spec §31 cases 3-8)."""

from app.modules.analysis.config import get_analysis_config
from app.modules.analysis.gaps import detect_requirement_gaps, gap_priority, impact_score
from app.modules.analysis.schemas import GapType, Priority
from app.modules.analysis.strengths import detect_requirement_strengths, prioritize_strengths
from app.modules.scoring.schemas import RequirementScoreResult, ScoringCategory

_CONFIG = get_analysis_config()


def _req(id="req_1", category=ScoringCategory.REQUIRED_SKILLS, status="MISSING", score=0.0, importance="REQUIRED", weight=1.0, critical=False, duplicate_of=None):
    return RequirementScoreResult(
        requirement_id=id, text=id, category=category, status=status, score=score,
        importance=importance, weight=weight, critical=critical, duplicate_of=duplicate_of,
    )


# --- Case 3: missing required skill ---

def test_missing_required_skill_is_a_gap_with_high_or_critical_priority():
    gaps = detect_requirement_gaps([_req(status="MISSING")], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    assert len(gaps) == 1
    assert gaps[0].type == GapType.MISSING_REQUIREMENT
    assert gaps[0].priority in (Priority.CRITICAL, Priority.HIGH)


# --- Case 7: critical gap ---

def test_critical_flag_forces_critical_priority():
    gaps = detect_requirement_gaps([_req(status="MISSING", critical=True)], {"REQUIRED_SKILLS": 0.01}, _CONFIG)
    assert gaps[0].priority == Priority.CRITICAL


# --- Case 8: optional gap ---

def test_optional_missing_skill_is_lower_priority_than_required():
    required_gaps = detect_requirement_gaps([_req(status="MISSING", importance="REQUIRED")], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    optional_gaps = detect_requirement_gaps(
        [_req(status="MISSING", importance="OPTIONAL", category=ScoringCategory.OTHER)], {"OTHER": 0.05}, _CONFIG
    )
    required_priority_rank = {Priority.CRITICAL: 3, Priority.HIGH: 2, Priority.MEDIUM: 1, Priority.LOW: 0}
    assert required_priority_rank[required_gaps[0].priority] > required_priority_rank[optional_gaps[0].priority]


# --- Case 4: partial requirement ---

def test_partial_requirement_is_a_gap():
    gaps = detect_requirement_gaps([_req(status="PARTIAL", score=0.6)], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    assert gaps[0].type == GapType.PARTIAL_REQUIREMENT
    assert gaps[0].details.what_is_satisfied is not None
    assert gaps[0].details.what_is_missing is not None


# --- Case 5: weak evidence ---

def test_weak_status_produces_weak_evidence_gap_not_missing():
    gaps = detect_requirement_gaps([_req(status="WEAK", score=0.35)], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    assert gaps[0].type == GapType.WEAK_EVIDENCE


# --- Case 6: unknown requirement never becomes a gap (spec §7) ---

def test_unknown_status_is_never_a_gap():
    gaps = detect_requirement_gaps([_req(status="UNKNOWN", score=0.5)], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    assert gaps == []


def test_very_strong_or_strong_status_is_never_a_gap():
    gaps = detect_requirement_gaps(
        [_req(status="STRONG", score=0.9), _req(id="req_2", status="VERY_STRONG", score=1.0)],
        {"REQUIRED_SKILLS": 0.28},
        _CONFIG,
    )
    assert gaps == []


def test_duplicate_requirement_is_not_a_gap():
    gaps = detect_requirement_gaps([_req(status="MISSING", duplicate_of="req_0")], {"REQUIRED_SKILLS": 0.28}, _CONFIG)
    assert gaps == []


def test_domain_knowledge_category_produces_domain_gap():
    gaps = detect_requirement_gaps(
        [_req(status="MISSING", category=ScoringCategory.DOMAIN_KNOWLEDGE)], {"DOMAIN_KNOWLEDGE": 0.07}, _CONFIG
    )
    assert gaps[0].type == GapType.DOMAIN_GAP


def test_experience_category_produces_experience_gap():
    gaps = detect_requirement_gaps(
        [_req(status="PARTIAL", category=ScoringCategory.EXPERIENCE)], {"EXPERIENCE": 0.18}, _CONFIG
    )
    assert gaps[0].type == GapType.EXPERIENCE_GAP


def test_qualifications_category_produces_qualification_gap():
    gaps = detect_requirement_gaps(
        [_req(status="MISSING", category=ScoringCategory.QUALIFICATIONS)], {"QUALIFICATIONS": 0.10}, _CONFIG
    )
    assert gaps[0].type == GapType.QUALIFICATION_GAP


# --- strengths ---

def test_strong_match_on_required_skill_is_a_strength():
    strengths = detect_requirement_strengths([_req(status="VERY_STRONG", score=1.0, importance="REQUIRED")], _CONFIG)
    assert len(strengths) == 1


def test_weak_or_missing_is_never_a_strength():
    strengths = detect_requirement_strengths(
        [_req(status="MISSING"), _req(id="req_2", status="WEAK"), _req(id="req_3", status="PARTIAL")], _CONFIG
    )
    assert strengths == []


def test_top_n_strengths_is_respected():
    reqs = [_req(id=f"req_{i}", status="VERY_STRONG", score=1.0) for i in range(10)]
    strengths = detect_requirement_strengths(reqs, _CONFIG)
    top = prioritize_strengths(strengths, _CONFIG)
    assert len(top) == _CONFIG.limits.top_n_strengths


def test_impact_score_and_priority_are_deterministic():
    req = _req(status="MISSING", importance="REQUIRED", weight=1.0)
    impact_1 = impact_score(req, 0.28, _CONFIG)
    impact_2 = impact_score(req, 0.28, _CONFIG)
    assert impact_1 == impact_2
    assert gap_priority(req, impact_1, _CONFIG) == gap_priority(req, impact_2, _CONFIG)
