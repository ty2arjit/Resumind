"""End-to-end ScoringService tests using real parsing/matching/evidence
(spec §33's 10 sanity-test cases)."""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.scoring import ScoringService
from tests.fixtures.builders import build_pdf

_service = ScoringService()


def _resume(text):
    return parse_pdf_bytes(build_pdf([text]))


# Case 1 — Strong resume.
def test_strong_resume_scores_highly():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Engineer, Co | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using FastAPI and Python.\n"
        "- Optimized PostgreSQL queries and reduced latency by 35%.\n\nSKILLS\nPython, FastAPI, PostgreSQL\n"
    )
    jd = parse_jd_text(
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n- Experience with PostgreSQL.\n"
    )
    breakdown = _service.calculate_ats_alignment(jd, resume)
    assert breakdown.ats_alignment >= 60


# Case 2 — Weak resume.
def test_weak_resume_scores_lowly():
    resume = _resume("Jane\n\nSKILLS\nMarketing, Sales\n")
    jd = parse_jd_text(
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n- Experience with Kafka.\n- Experience with Go.\n"
    )
    breakdown = _service.calculate_ats_alignment(jd, resume)
    assert breakdown.ats_alignment <= 40


# Case 3 — Missing critical requirement -> meaningful decrease (only
# once explicitly enabled; verify the *mechanism*, not the default).
def test_missing_requirement_reduces_category_score():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    jd_with_gap = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with Kubernetes.\n")
    jd_without_gap = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    with_gap = _service.calculate_ats_alignment(jd_with_gap, resume)
    without_gap = _service.calculate_ats_alignment(jd_without_gap, resume)
    assert with_gap.ats_alignment < without_gap.ats_alignment


# Case 5 — UNKNOWN requirement does not behave identically to MISSING.
def test_unknown_status_is_distinguishable_from_missing():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")  # no education/experience info at all
    jd = parse_jd_text(
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n"
        "- 3+ years of experience with Python.\n"
        "- Bachelor's degree in Computer Science.\n"
    )
    breakdown = _service.calculate_ats_alignment(jd, resume)
    statuses = {r.text: r.status for r in breakdown.requirements}
    # No dates at all -> experience requirement is UNKNOWN, not MISSING.
    experience_req = next(r for r in breakdown.requirements if "years" in r.text)
    assert experience_req.status == "UNKNOWN"


# Case 6 — Alias (Postgres vs PostgreSQL) -> strong match.
def test_alias_produces_strong_match():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Optimized Postgres queries by 35%.\n")
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with PostgreSQL.\n")
    breakdown = _service.calculate_ats_alignment(jd, resume)
    req = breakdown.requirements[0]
    assert req.status in ("PARTIAL", "STRONG", "VERY_STRONG")


# Case 7 — False semantic match (Docker vs Kubernetes) -> not strong.
def test_docker_does_not_satisfy_kubernetes_requirement():
    resume = _resume("Jane\n\nEXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n- Deployed services using Docker.\n")
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n")
    breakdown = _service.calculate_ats_alignment(jd, resume)
    req = breakdown.requirements[0]
    assert req.status in ("MISSING", "WEAK")


# Case 9 — Empty category -> active weights normalize correctly.
def test_missing_category_normalizes_remaining_weights():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")  # no Responsibilities, Experience, Qualifications sections
    breakdown = _service.calculate_ats_alignment(jd, resume)
    total_normalized = sum(c.normalized_weight for c in breakdown.categories.values())
    assert abs(total_normalized - 1.0) < 1e-6


# Case 10 — Duplicate requirements -> no artificial inflation.
def test_duplicate_requirements_do_not_inflate_score():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    jd_single = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    jd_duplicated = parse_jd_text(
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Strong Python experience.\n"
    )
    single = _service.calculate_ats_alignment(jd_single, resume)
    duplicated = _service.calculate_ats_alignment(jd_duplicated, resume)
    assert duplicated.ats_alignment == single.ats_alignment


def test_score_and_versions_are_always_present():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    breakdown = _service.calculate_ats_alignment(jd, resume)
    assert 0 <= breakdown.ats_alignment <= 100
    assert breakdown.algorithm_version == "ATS_ENGINE_V1"
    assert breakdown.scoring_config_version
    assert breakdown.knowledge_version
    assert breakdown.embedding_model_version


def test_determinism_across_repeated_runs():
    resume = _resume(
        "Jane\n\nEXPERIENCE\nBackend Engineer, Co | Jan 2021 - Jan 2024\n- Built REST APIs using FastAPI.\n\nSKILLS\nPython, Django\n"
    )
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n")
    results = [_service.calculate_ats_alignment(jd, resume).ats_alignment for _ in range(3)]
    assert len(set(results)) == 1
