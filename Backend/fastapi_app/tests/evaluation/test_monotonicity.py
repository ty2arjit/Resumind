"""Score monotonicity tests (spec Phase 13 §23) — adding genuinely more
relevant evidence should never decrease the score. Not required to be
strictly linear, only sensibly non-decreasing."""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.scoring import ScoringService
from tests.fixtures.builders import build_pdf

_service = ScoringService()


def test_increasing_postgresql_evidence_quality_does_not_decrease_score():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with PostgreSQL.\n")

    v1_no_evidence = "Jane Doe\njane@example.com\n\nSKILLS\nJavaScript, HTML\n"
    v2_skill_mention = "Jane Doe\njane@example.com\n\nSKILLS\nPostgreSQL\n"
    v3_strong_evidence = (
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Optimized PostgreSQL queries and reduced latency by 35% through indexing.\n\nSKILLS\nPostgreSQL\n"
    )

    score_v1 = _service.calculate_ats_alignment(jd, parse_pdf_bytes(build_pdf([v1_no_evidence]))).ats_alignment
    score_v2 = _service.calculate_ats_alignment(jd, parse_pdf_bytes(build_pdf([v2_skill_mention]))).ats_alignment
    score_v3 = _service.calculate_ats_alignment(jd, parse_pdf_bytes(build_pdf([v3_strong_evidence]))).ats_alignment

    assert score_v3 >= score_v2 >= score_v1
