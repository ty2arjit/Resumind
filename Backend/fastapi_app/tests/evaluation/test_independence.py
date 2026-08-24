"""Independence tests (spec Phase 13 §22, §20) — the same resume must
produce ~identical Resume Quality regardless of JD, and Position/Domain
Fit must respond independently to position-only vs domain-only evidence.
These are top-level regression guards; the underlying properties are
also covered per-module in Phase 8/9's own test suites."""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.resume_quality import ResumeQualityService
from app.modules.target_profile import TargetProfileService
from tests.fixtures.builders import build_pdf

_RESUME_TEXT = (
    "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
    "- Built REST APIs using Python and FastAPI.\n\nSKILLS\nPython, FastAPI\n"
)


def test_resume_quality_is_identical_regardless_of_which_jd_is_analyzed():
    resume = parse_pdf_bytes(build_pdf([_RESUME_TEXT]))
    quality_service = ResumeQualityService()

    result_without_jd = quality_service.analyze(resume)

    parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    parse_jd_text("Data Scientist\n\nREQUIRED QUALIFICATIONS\n- Experience with R and Kubernetes.\n")
    result_after_two_jds = quality_service.analyze(resume)

    assert result_without_jd.resume_quality == result_after_two_jds.resume_quality
    assert result_without_jd.dimension_scores == result_after_two_jds.dimension_scores


def test_position_fit_and_domain_fit_respond_independently():
    strong_position_no_domain_resume = (
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python and Java, developing scalable backend services.\n"
        "- Designed PostgreSQL database systems and optimized query performance.\n\n"
        "SKILLS\nPython, Java, SQL, REST APIs, PostgreSQL, Redis, Docker, AWS\n"
    )
    resume = parse_pdf_bytes(build_pdf([strong_position_no_domain_resume]))
    target_service = TargetProfileService()
    result = target_service.analyze("Backend Developer", resume, "FinTech")

    # Strong, generic backend evidence with no FinTech-specific signal
    # (payments/transactions/compliance) should score Position Fit
    # meaningfully above Domain Fit.
    assert result.scores.position_fit > result.scores.domain_fit
