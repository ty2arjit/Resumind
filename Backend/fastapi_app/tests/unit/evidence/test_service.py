"""Exercises the full EvidenceService, including the real embedding
model (spec §28-29) — each test name maps to one of the 15 required
scenarios."""

from app.models.enums import MatchStrength
from app.modules.evidence import EvidenceService
from app.modules.evidence.schemas import EvidenceStrength
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf

_service = EvidenceService()


def _resume(text):
    return parse_pdf_bytes(build_pdf([text]))


# 1. Strong experience evidence.
def test_strong_experience_evidence():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Optimized PostgreSQL queries and reduced latency by 35%.\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Experience with PostgreSQL", ["PostgreSQL"], resume)
    assert result.evidence
    assert result.evidence[0].strength != EvidenceStrength.MISSING


# 2. Weak skills-only evidence.
def test_weak_skills_only_evidence():
    resume = _resume("Jane\n\nSKILLS\nPostgreSQL\n")
    result = _service.retrieve_requirement_evidence("req_1", "Experience with PostgreSQL", ["PostgreSQL"], resume)
    assert result.evidence
    assert result.evidence[0].section.value == "SKILLS_SECTION"


# 3. Strong project evidence.
def test_strong_project_evidence():
    resume = _resume("Jane\n\nPROJECTS\nResumind | PostgreSQL\n- Optimized PostgreSQL queries for the pipeline.\n")
    result = _service.retrieve_requirement_evidence("req_1", "PostgreSQL", ["PostgreSQL"], resume)
    assert any(e.section.value == "PROJECT_BULLET" for e in result.evidence)


# 4. Multiple supporting evidence items.
def test_multiple_supporting_evidence_items():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Built FastAPI APIs using Python.\n"
        "- Implemented Redis caching in a Python backend.\n\n"
        "SKILLS\nPython\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Backend development with Python", ["Python"], resume, top_k=5)
    assert len(result.evidence) >= 2


# 5. Duplicate evidence.
def test_duplicate_bullets_do_not_multiply_evidence():
    """The two mentions must be non-adjacent (different sections) — Phase
    2's own text cleaning already collapses literally-adjacent duplicate
    lines, so an adjacent pair would never reach this layer to test it."""
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Built REST APIs using Python.\n\n"
        "PROJECTS\nSide Project | Python\n"
        "- Built REST APIs using Python.\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Python", ["Python"], resume, top_k=5)
    texts = [e.text for e in result.evidence]
    assert len(texts) == len(set(texts))
    assert result.warnings  # duplicate suppression is reported


# 6. Keyword stuffing.
def test_keyword_stuffing_does_not_scale_aggregate_linearly():
    one_mention_resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Built backend services using Python.\n"
    )
    five_mentions_resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Built backend services using Python.\n"
        "- Used Python for scripting tasks.\n"
        "- Used Python to automate deployments.\n"
        "- Wrote Python unit tests.\n"
        "- Used Python for data analysis.\n"
    )
    one = _service.retrieve_requirement_evidence("req_1", "Python", ["Python"], one_mention_resume, top_k=5)
    five = _service.retrieve_requirement_evidence("req_1", "Python", ["Python"], five_mentions_resume, top_k=5)

    assert five.aggregated_evidence_strength > one.aggregated_evidence_strength
    assert five.aggregated_evidence_strength < one.aggregated_evidence_strength * 5


# 7. Technology mismatch.
def test_technology_mismatch_produces_missing_or_weak():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Deployed services using Docker.\n")
    result = _service.retrieve_requirement_evidence("req_1", "Kubernetes", ["Kubernetes"], resume)
    assert result.match_result in (MatchStrength.MISSING, MatchStrength.WEAK, MatchStrength.UNKNOWN)


# 8. Action match.
def test_action_match_signal_present():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Developed REST APIs using FastAPI.\n")
    result = _service.retrieve_requirement_evidence("req_1", "Develop REST APIs", [], resume)
    experience_evidence = next(e for e in result.evidence if e.section.value == "EXPERIENCE_BULLET")
    assert experience_evidence.signals.action_match is not None


# 9. Object match.
def test_object_match_signal_present():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Built REST APIs using FastAPI.\n")
    result = _service.retrieve_requirement_evidence("req_1", "Develop REST APIs", [], resume)
    assert result.evidence[0].signals.object_match is not None


# 10. Metric detection.
def test_metric_presence_detected():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Reduced latency by 35% using caching.\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Performance optimization", [], resume)
    assert result.evidence[0].signals.metric_presence == 1.0


# 11. Experience duration evidence.
def test_experience_duration_evidence():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Engineer, Co | Jan 2021 - Jan 2024\n- Built backend services using Python.\n")
    result = _service.retrieve_requirement_evidence(
        "req_1", "3+ years of Python experience", ["Python"], resume,
        required_years=3.0, experience_context_technologies=["Python"], experience_context_text="Python",
    )
    assert result.experience is not None
    assert result.experience.detected_relevant_years == 3.0


# 12. Qualification evidence.
def test_qualification_evidence():
    resume = _resume("Jane\n\nEDUCATION\nNIT Rourkela\nB.Tech in Computer Science, 2020 - 2024\n")
    result = _service.retrieve_requirement_evidence(
        "req_1", "Bachelor's degree in Computer Science", [], resume,
        requirement_degree="Bachelor's", requirement_field="Computer Science",
    )
    assert result.qualification is not None
    assert result.qualification.matched is True


# 13. Unknown evidence.
def test_no_resume_evidence_is_unknown():
    resume = _resume("Jane\n")
    result = _service.retrieve_requirement_evidence("req_1", "Kubernetes", ["Kubernetes"], resume)
    assert result.match_result == MatchStrength.UNKNOWN


# 14. Evidence ranking.
def test_experience_evidence_ranks_above_bare_skills_mention():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Optimized PostgreSQL queries and reduced latency by 35%.\n\n"
        "SKILLS\nPostgreSQL\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Experience with PostgreSQL", ["PostgreSQL"], resume, top_k=5)
    sections = [e.section.value for e in result.evidence]
    assert sections.index("EXPERIENCE_BULLET") < sections.index("SKILLS_SECTION")


# 15. Top-K behavior.
def test_top_k_limits_returned_evidence():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
        "- Built APIs using Python.\n- Used Python for scripting.\n- Wrote Python tests.\n- Automated Python deployments.\n"
    )
    result = _service.retrieve_requirement_evidence("req_1", "Python", ["Python"], resume, top_k=2)
    assert len(result.evidence) <= 2


def test_determinism():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Optimized PostgreSQL queries by 35%.\n"
    )
    results = [
        _service.retrieve_requirement_evidence("req_1", "Experience with PostgreSQL", ["PostgreSQL"], resume)
        for _ in range(3)
    ]
    assert len({r.match_result for r in results}) == 1
    assert len({round(r.aggregated_evidence_strength, 6) for r in results}) == 1
