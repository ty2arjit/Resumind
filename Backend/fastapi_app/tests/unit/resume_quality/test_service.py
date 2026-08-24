"""End-to-end ResumeQualityService tests using real PDF parsing (spec
§33-36)."""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.resume_quality import ResumeQualityService
from tests.fixtures.builders import build_pdf

_service = ResumeQualityService()


def _resume(text):
    return parse_pdf_bytes(build_pdf([text]))


def test_score_is_bounded_0_to_100():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    result = _service.analyze(resume)
    assert 0 <= result.resume_quality <= 100


def test_versions_are_always_present():
    resume = _resume("Jane\n\nSKILLS\nPython, Django\n")
    result = _service.analyze(resume)
    assert result.resume_quality_algorithm_version == "RESUME_QUALITY_V1"
    assert result.resume_quality_config_version


def test_missing_optional_information_does_not_destroy_score():
    resume = _resume(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using FastAPI and Python.\n- Optimized PostgreSQL queries, reducing latency by 35%.\n\n"
        "SKILLS\nPython, FastAPI, PostgreSQL\n"
    )
    result = _service.analyze(resume)
    assert result.resume_quality >= 60


def test_strong_resume_scores_higher_than_weak_resume():
    strong = _resume(
        "Jane Doe\njane@example.com | 555-1234 | linkedin.com/in/jane\n\n"
        "EXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using FastAPI and Python, serving 50K daily users.\n"
        "- Optimized PostgreSQL queries using indexing, reducing API latency by 35%.\n\n"
        "PROJECTS\nAutomation Tool | Python\n- Automated deployment pipeline using Docker and GitHub Actions.\n\n"
        "EDUCATION\nB.Tech Computer Science, XYZ University | 2017 - 2021\n\n"
        "SKILLS\nPython, FastAPI, PostgreSQL, Docker\n"
    )
    weak = _resume("Jane\n\nSKILLS\nMarketing, Sales\n")
    strong_result = _service.analyze(strong)
    weak_result = _service.analyze(weak)
    assert strong_result.resume_quality > weak_result.resume_quality


# --- Independence test (spec §34) ---

def test_resume_quality_is_independent_of_job_description():
    resume = _resume(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using FastAPI and Python.\n\nSKILLS\nPython, FastAPI\n"
    )
    result_no_jd = _service.analyze(resume)

    parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    parse_jd_text("Data Scientist\n\nREQUIRED QUALIFICATIONS\n- Experience with R and Kubernetes.\n")

    result_after_jds = _service.analyze(resume)

    assert result_no_jd.resume_quality == result_after_jds.resume_quality
    assert result_no_jd.dimension_scores == result_after_jds.dimension_scores


# --- Determinism test (spec §35) ---

def test_determinism_across_repeated_runs():
    resume = _resume(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using FastAPI and Python.\n\nSKILLS\nPython, FastAPI\n"
    )
    results = [_service.analyze(resume).resume_quality for _ in range(3)]
    assert len(set(results)) == 1


def test_parser_failure_meaningfully_reduces_parseability():
    from tests.fixtures.builders import build_empty_pdf

    empty_resume = parse_pdf_bytes(build_empty_pdf())
    result = _service.analyze(empty_resume)
    assert result.dimension_scores.parseability < 0.5
