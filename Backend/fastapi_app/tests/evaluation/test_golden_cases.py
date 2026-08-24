"""Golden test cases (spec Phase 13 §38) — a small, manually verified set
representing one example each of: strong match, weak match, missing
requirement, partial match, semantic match, false semantic match,
keyword stuffing, critical requirement. Pinned as permanent regression
fixtures — a future change that breaks any of these must be treated as
a deliberate, reviewed calibration change, not an accident.
"""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.scoring import ScoringService
from tests.fixtures.builders import build_pdf

_service = ScoringService()


def _first_status(resume_text, jd_text):
    resume = parse_pdf_bytes(build_pdf([resume_text]))
    jd = parse_jd_text(jd_text)
    breakdown = _service.calculate_ats_alignment(jd, resume)
    return breakdown.requirements[0].status


def test_golden_strong_match():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2020 - Jan 2024\n"
        "- Built backend systems using Python.\n\nSKILLS\nPython\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- 3+ years of experience with Python.\n",
    )
    assert status == "VERY_STRONG"


def test_golden_weak_match():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Intern, Acme | Jun 2023 - Aug 2023\n"
        "- Deployed services using Docker.\n\nSKILLS\nDocker\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
    )
    assert status in ("MISSING", "WEAK")


def test_golden_missing_requirement():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nSKILLS\nMarketing, Sales\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
    )
    assert status == "MISSING"


def test_golden_partial_match():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nAnalyst, Acme | Jan 2022 - Jan 2024\n"
        "- Analyzed sales data.\n\nSKILLS\nSQL, Excel\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with SQL.\n",
    )
    assert status in ("PARTIAL", "WEAK", "STRONG")


def test_golden_semantic_evidence_match():
    # NOTE: a technology-anchored paraphrase (FastAPI appears in both JD
    # and resume) is used here rather than a pure prose paraphrase with
    # no shared technology term — see docs/EVALUATION_REPORT.md's error
    # analysis for CASE_C1, a documented false negative where a
    # technology-less responsibility paraphrase ("Optimize database
    # performance." vs "Optimized PostgreSQL queries...") still scores
    # MISSING despite 0.61 semantic similarity, because Phase 5's fusion
    # weighting under-credits semantic-only signal for that case shape.
    status = _first_status(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built FastAPI services handling 10K requests per day.\n\nSKILLS\nFastAPI\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience building REST APIs with FastAPI.\n",
    )
    assert status != "MISSING"


def test_golden_false_semantic_match_is_rejected():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Intern, Acme | Jun 2023 - Aug 2023\n"
        "- Deployed services using Docker.\n\nSKILLS\nDocker\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
    )
    assert status not in ("STRONG", "VERY_STRONG")


def test_golden_keyword_stuffing_does_not_reach_very_strong():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nSKILLS\n" + ", ".join(["Python"] * 20) + "\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n",
    )
    assert status != "VERY_STRONG"


def test_golden_critical_requirement_missing():
    status = _first_status(
        "Jane Doe\njane@example.com\n\nSKILLS\nPython, Django\n",
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
    )
    assert status == "MISSING"
