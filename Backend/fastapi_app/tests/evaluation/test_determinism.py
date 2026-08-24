"""Determinism tests (spec Phase 13 §32) — running the same analysis
multiple times must produce identical results across the whole pipeline,
not just the final score."""

from app.modules.analysis import AnalysisService
from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf

_service = AnalysisService()

_RESUME_TEXT = (
    "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
    "- Built REST APIs using Python and FastAPI.\n\nSKILLS\nPython, FastAPI\n"
)


def test_full_analysis_pipeline_is_deterministic_across_repeated_runs():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n")
    resume = parse_pdf_bytes(build_pdf([_RESUME_TEXT]))

    results = [_service.run_jd_analysis(jd, resume) for _ in range(3)]

    ats_scores = {r.scores.ats_alignment for r in results}
    quality_scores = {r.scores.resume_quality for r in results}
    gap_counts = {len(r.gaps) for r in results}
    strength_counts = {len(r.strengths) for r in results}
    recommendation_counts = {len(r.recommendations) for r in results}
    requirement_statuses = {tuple(sorted((req.requirement_id, req.status) for req in r.requirements)) for r in results}

    assert len(ats_scores) == 1
    assert len(quality_scores) == 1
    assert len(gap_counts) == 1
    assert len(strength_counts) == 1
    assert len(recommendation_counts) == 1
    assert len(requirement_statuses) == 1
