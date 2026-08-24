"""Recommendation generation, no-fabrication, and traceability tests
(spec §31 cases 14-15)."""

from app.modules.analysis.config import get_analysis_config
from app.modules.analysis.recommendations import generate_recommendations_from_gaps, prioritize_recommendations
from app.modules.analysis.schemas import AnalysisSource, Gap, GapDetail, GapType, Priority, RecommendationType

_CONFIG = get_analysis_config()


def _gap(text="Kubernetes", gap_type=GapType.MISSING_REQUIREMENT, priority=Priority.CRITICAL, message_key="MISSING_REQUIRED_SKILL", requirement_id="req_1"):
    return Gap(
        type=gap_type, priority=priority, requirement_id=requirement_id, text=text, category="REQUIRED_SKILLS",
        status="MISSING", message_key=message_key, details=GapDetail(),
    )


# --- Case 15: no-fabrication behavior ---

def test_missing_requirement_recommendation_never_asserts_the_skill_should_simply_be_added():
    gap = _gap()
    recommendations = generate_recommendations_from_gaps([gap])
    message = recommendations[0].message
    assert "Add Kubernetes to your resume" not in message
    assert "if you genuinely have this experience" in message.lower()
    assert "Kubernetes" in message


def test_recommendation_never_claims_the_candidate_has_the_skill():
    gap = _gap(text="Rust", message_key="MISSING_REQUIRED_SKILL")
    recommendations = generate_recommendations_from_gaps([gap])
    message = recommendations[0].message.lower()
    assert "you have rust experience" not in message
    assert "if" in message  # conditional framing, never asserted as fact


# --- Case 14: recommendation traceability ---

def test_recommendation_is_traceable_to_its_source_gap():
    gap = _gap(requirement_id="req_42")
    recommendations = generate_recommendations_from_gaps([gap])
    rec = recommendations[0]
    assert rec.requirement_id == "req_42"
    assert rec.reason_code == GapType.MISSING_REQUIREMENT.value
    assert rec.message_key == "MISSING_REQUIRED_SKILL"
    assert rec.type == RecommendationType.ADDRESS_MISSING_REQUIREMENT


def test_weak_evidence_gap_maps_to_strengthen_evidence_recommendation():
    gap = _gap(gap_type=GapType.WEAK_EVIDENCE, message_key="STRENGTHEN_SKILL_EVIDENCE", priority=Priority.HIGH)
    recommendations = generate_recommendations_from_gaps([gap])
    assert recommendations[0].type == RecommendationType.STRENGTHEN_EVIDENCE


def test_domain_gap_maps_to_improve_domain_evidence_recommendation():
    gap = _gap(gap_type=GapType.DOMAIN_GAP, message_key="MISSING_DOMAIN_KNOWLEDGE", priority=Priority.HIGH)
    recommendations = generate_recommendations_from_gaps([gap])
    assert recommendations[0].type == RecommendationType.IMPROVE_DOMAIN_EVIDENCE


def test_resume_quality_gap_maps_to_parsing_recommendation():
    gap = Gap(
        type=GapType.RESUME_QUALITY_GAP, priority=Priority.HIGH, text="POSSIBLE_SCANNED_PDF",
        category="PARSEABILITY", status="HIGH", message_key="PARSING_WARNING", source=AnalysisSource.RESUME_QUALITY,
    )
    recommendations = generate_recommendations_from_gaps([gap])
    assert recommendations[0].type == RecommendationType.IMPROVE_PARSING
    assert recommendations[0].source == AnalysisSource.RESUME_QUALITY


def test_top_n_recommendations_is_respected():
    gaps = [_gap(requirement_id=f"req_{i}", priority=Priority.HIGH) for i in range(10)]
    recommendations = generate_recommendations_from_gaps(gaps)
    top = prioritize_recommendations(recommendations, _CONFIG)
    assert len(top) == _CONFIG.limits.top_n_recommendations


def test_critical_recommendations_are_ranked_above_low_priority_ones():
    gaps = [_gap(requirement_id="req_low", priority=Priority.LOW), _gap(requirement_id="req_critical", priority=Priority.CRITICAL)]
    recommendations = generate_recommendations_from_gaps(gaps)
    top = prioritize_recommendations(recommendations, _CONFIG)
    assert top[0].priority == Priority.CRITICAL
