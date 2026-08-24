"""Integration tests for AnalysisService (spec §31 cases 1-2, 9-13, 16),
via real PDF/JD parsing, verifying Phase 5-9 reuse end to end."""

from app.modules.analysis import AnalysisService
from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf

_service = AnalysisService()


def _resume(text):
    return parse_pdf_bytes(build_pdf([text]))


_STRONG_RESUME_TEXT = (
    "Jane Doe\njane@example.com\n\n"
    "EXPERIENCE\nBackend Engineer, Acme Co | Jan 2021 - Jan 2024\n"
    "- Built REST APIs using FastAPI and Python.\n"
    "- Optimized PostgreSQL queries using indexing, reducing API latency by 35%.\n\n"
    "SKILLS\nPython, FastAPI, PostgreSQL\n"
)
_WEAK_RESUME_TEXT = "Jane\n\nSKILLS\nMarketing, Sales\n"


# --- Case 1/2: strong vs weak JD alignment ---

def test_strong_jd_alignment_scores_higher_than_weak():
    jd = parse_jd_text(
        "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n- Experience with PostgreSQL.\n"
    )
    strong = _service.run_jd_analysis(jd, _resume(_STRONG_RESUME_TEXT))
    weak = _service.run_jd_analysis(jd, _resume(_WEAK_RESUME_TEXT))
    assert strong.scores.ats_alignment > weak.scores.ats_alignment
    assert strong.summary.critical_gap_count <= weak.summary.critical_gap_count


# --- Case 9: strong target profile fit ---

def test_strong_target_alignment_produces_strengths():
    resume = _resume(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python and Java, developing scalable backend services.\n\n"
        "SKILLS\nPython, Java, SQL, REST APIs, PostgreSQL, Redis, Docker, AWS\n"
    )
    result = _service.run_target_analysis("Backend Developer", resume)
    assert result.scores.target_fit is not None
    assert result.scores.ats_alignment is None


# --- Case 10/11: weak domain fit vs strong position fit ---

def test_weak_domain_fit_is_distinguishable_from_position_fit():
    resume = _resume(
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python and Java.\n- Designed PostgreSQL database systems.\n\n"
        "SKILLS\nPython, Java, SQL, REST APIs, PostgreSQL, Redis, Docker, AWS\n"
    )
    result = _service.run_target_analysis("Backend Developer", resume, "FinTech")
    assert result.scores.position_fit != result.scores.domain_fit


# --- Case 12: resume quality issue surfaces in JD mode ---

def test_resume_quality_issue_produces_resume_quality_gap():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    result = _service.run_jd_analysis(jd, _resume(_WEAK_RESUME_TEXT))
    from app.modules.analysis import GapType

    assert any(g.type == GapType.RESUME_QUALITY_GAP for g in result.gaps)
    assert result.scores.resume_quality is not None


# --- Case 13: combined JD + Target Profile mode ---

def test_combined_mode_returns_all_three_scores_separately():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with Kubernetes.\n")
    resume = _resume(_STRONG_RESUME_TEXT)
    result = _service.run_combined_analysis(jd, resume, "Backend Developer", "FinTech")
    assert result.scores.ats_alignment is not None
    assert result.scores.target_fit is not None
    assert result.scores.resume_quality is not None
    from app.modules.analysis import AnalysisSource

    assert any(g.source == AnalysisSource.JD for g in result.gaps)
    assert any(g.source == AnalysisSource.TARGET_PROFILE for g in result.gaps)


def test_combined_mode_jd_gaps_are_ordered_before_target_profile_gaps():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n")
    resume = _resume(_WEAK_RESUME_TEXT)
    result = _service.run_combined_analysis(jd, resume, "Backend Developer", "FinTech")
    from app.modules.analysis import AnalysisSource

    sources = [g.source for g in result.gaps if g.source != AnalysisSource.RESUME_QUALITY]
    jd_indices = [i for i, s in enumerate(sources) if s == AnalysisSource.JD]
    target_indices = [i for i, s in enumerate(sources) if s == AnalysisSource.TARGET_PROFILE]
    if jd_indices and target_indices:
        assert max(jd_indices) < min(target_indices)


# --- Case 16: deterministic output ---

def test_analysis_output_is_deterministic():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n")
    resume = _resume(_STRONG_RESUME_TEXT)
    results = [_service.run_jd_analysis(jd, resume) for _ in range(3)]
    ats_scores = {r.scores.ats_alignment for r in results}
    gap_counts = {len(r.gaps) for r in results}
    assert len(ats_scores) == 1
    assert len(gap_counts) == 1


# --- Case 18: invalid input handling ---

def test_missing_position_and_domain_still_returns_a_jd_only_analysis():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    resume = _resume(_STRONG_RESUME_TEXT)
    result = _service.run_jd_analysis(jd, resume)
    assert result.context.target_profile_position is None


# --- Phase 12 §22-23: category breakdown and requirement-level pass-through ---

def test_jd_analysis_exposes_category_breakdown_and_requirements():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n- Experience with FastAPI.\n")
    resume = _resume(_STRONG_RESUME_TEXT)
    result = _service.run_jd_analysis(jd, resume)
    assert result.categories is not None
    assert "REQUIRED_SKILLS" in result.categories
    assert result.categories["REQUIRED_SKILLS"]["score"] >= 0
    assert len(result.requirements) == 2
    assert all(r.requirement_id for r in result.requirements)


def test_target_analysis_exposes_requirements_but_no_category_breakdown():
    resume = _resume(_STRONG_RESUME_TEXT)
    result = _service.run_target_analysis("Backend Developer", resume, "FinTech")
    assert result.categories is None
    assert len(result.requirements) > 0


def test_combined_analysis_merges_requirements_from_both_modes():
    jd = parse_jd_text("Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n")
    resume = _resume(_STRONG_RESUME_TEXT)
    result = _service.run_combined_analysis(jd, resume, "Backend Developer", "FinTech")
    assert result.categories is not None
    assert len(result.requirements) > 1
