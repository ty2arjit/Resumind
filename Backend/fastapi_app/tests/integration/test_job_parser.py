"""End-to-end JD parser tests (spec §24). Each test name maps to one of
the 13 required scenarios; assertions check structured output, not just
"didn't crash".
"""

from app.modules.job.parser import parse_pdf_bytes, parse_text
from app.modules.job.schemas import JDCanonicalSection, JDWarningCode
from app.models.enums import ImportanceLevel, RequirementType
from app.modules.resume.schemas import ExtractionStatus
from tests.fixtures.builders import build_empty_pdf, build_pdf


# 1. Simple JD.
def test_simple_jd():
    jd = parse_text("Backend Engineer\n\nSKILLS\nPython, FastAPI, PostgreSQL\n")
    assert jd.metadata.title == "Backend Engineer"
    assert "Python" in jd.skills


# 2. JD with Responsibilities + Requirements.
def test_jd_with_responsibilities_and_requirements():
    text = (
        "Backend Engineer\n\n"
        "RESPONSIBILITIES\n"
        "- Design scalable backend services.\n"
        "- Develop REST APIs using FastAPI.\n\n"
        "REQUIREMENTS\n"
        "- Strong experience with Python.\n"
        "- Experience with PostgreSQL.\n"
    )
    jd = parse_text(text)
    responsibility_types = [r.type for r in jd.requirements if r.source_section == JDCanonicalSection.RESPONSIBILITIES]
    assert RequirementType.RESPONSIBILITY in responsibility_types
    assert len(jd.responsibilities) == 2
    skill_reqs = [r for r in jd.requirements if r.type == RequirementType.SKILL]
    assert len(skill_reqs) == 2


# 3. JD with Required vs Preferred sections.
def test_required_vs_preferred_sections():
    text = (
        "Backend Engineer\n\n"
        "REQUIRED QUALIFICATIONS\n"
        "- Experience with Python.\n\n"
        "PREFERRED QUALIFICATIONS\n"
        "- Experience with Kubernetes.\n"
    )
    jd = parse_text(text)
    required = [r for r in jd.requirements if "Python" in r.technologies]
    preferred = [r for r in jd.requirements if "Kubernetes" in r.technologies]
    assert required[0].importance == ImportanceLevel.REQUIRED
    assert preferred[0].importance == ImportanceLevel.PREFERRED
    assert preferred[0].type == RequirementType.PREFERRED_SKILL


# 4. JD with experience requirements.
def test_jd_with_experience_requirements():
    text = "Backend Engineer\n\nREQUIREMENTS\n- 3+ years of experience with Python development.\n"
    jd = parse_text(text)
    assert len(jd.experience_requirements) == 1
    assert jd.experience_requirements[0].min_years == 3.0
    exp_reqs = [r for r in jd.requirements if r.type == RequirementType.EXPERIENCE]
    assert len(exp_reqs) == 1


# 5. JD with education requirements.
def test_jd_with_education_requirements():
    text = "Backend Engineer\n\nQUALIFICATIONS\n- Bachelor's degree in Computer Science or related field.\n"
    jd = parse_text(text)
    assert len(jd.qualifications) == 1
    assert jd.qualifications[0].degree == "Bachelor's"


# 6. JD containing multiple technologies.
def test_jd_with_multiple_technologies():
    text = "Backend Engineer\n\nSKILLS\nPython, FastAPI, PostgreSQL, Docker, AWS, Kubernetes, Redis, Kafka\n"
    jd = parse_text(text)
    for tech in ("Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Kubernetes", "Redis", "Kafka"):
        assert tech in jd.skills


# 7. JD with AND/OR requirements.
def test_jd_with_and_or_requirements():
    text = (
        "Backend Engineer\n\nREQUIREMENTS\n"
        "- Experience with Python and FastAPI.\n"
        "- Experience with AWS, Azure, or GCP.\n"
    )
    jd = parse_text(text)
    and_reqs = [r for r in jd.requirements if r.operator is not None and r.operator.value == "AND"]
    or_reqs = [r for r in jd.requirements if r.operator is not None and r.operator.value == "OR"]
    assert len(and_reqs) == 1
    assert len(or_reqs) == 1


# 8. JD with missing sections.
def test_jd_with_missing_sections_raises_warnings_not_errors():
    jd = parse_text("Backend Engineer\n\nSKILLS\nPython\n")
    codes = {w.code for w in jd.warnings}
    assert JDWarningCode.MISSING_EXPECTED_SECTION in codes


# 9. JD with unusual capitalization.
def test_unusual_heading_capitalization():
    text = "Backend Engineer\n\nkey responsibilities:\n- Build scalable systems.\n"
    jd = parse_text(text)
    assert any(s.canonical_type == JDCanonicalSection.RESPONSIBILITIES for s in jd.sections)


# 10. JD with duplicated requirements.
def test_jd_with_duplicated_requirements():
    text = (
        "Backend Engineer\n\nREQUIREMENTS\n"
        "- Experience with Python.\n"
        "- Strong Python experience.\n"
    )
    jd = parse_text(text)
    codes = {w.code for w in jd.warnings}
    assert JDWarningCode.DUPLICATE_REQUIREMENTS in codes
    # Spec §19: preserve original text — duplicates are flagged, not removed.
    assert len(jd.requirements) == 2


# 11. JD provided as plain text.
def test_jd_as_plain_text_input():
    jd = parse_text("We need someone with strong Python and FastAPI experience.")
    assert jd.document.format.value == "text"
    assert any("Python" in r.technologies for r in jd.requirements)


# 12. Malformed/empty JD.
def test_empty_text_jd():
    jd = parse_text("")
    assert jd.document.extraction_status == ExtractionStatus.EMPTY
    assert jd.requirements == []


def test_empty_pdf_jd():
    jd = parse_pdf_bytes(build_empty_pdf())
    assert jd.document.extraction_status == ExtractionStatus.EMPTY
    assert any(w.code == JDWarningCode.EMPTY_DOCUMENT for w in jd.warnings)


def test_low_text_pdf_flags_possible_scanned_document():
    jd = parse_pdf_bytes(build_pdf(["Hi"]))
    assert jd.document.extraction_status == ExtractionStatus.LOW_TEXT
    codes = {w.code for w in jd.warnings}
    assert JDWarningCode.POSSIBLE_SCANNED_PDF in codes


# 13. Low-confidence/ambiguous requirements.
def test_low_confidence_requirement_flagged():
    text = "Backend Engineer\n\nSKILLS\n- Knowledge of PostgreSQL.\n"
    jd = parse_text(text)
    codes = {w.code for w in jd.warnings}
    assert JDWarningCode.LOW_CONFIDENCE_CLASSIFICATION in codes
    pg_req = next(r for r in jd.requirements if "PostgreSQL" in r.technologies)
    assert pg_req.importance == ImportanceLevel.UNKNOWN


# PDF input (spec §1)
def test_pdf_jd_parses_end_to_end():
    text = (
        "Backend Engineer\n\nRESPONSIBILITIES\n- Build scalable systems.\n\n"
        "REQUIREMENTS\n- Strong experience with Python and PostgreSQL.\n"
    )
    jd = parse_pdf_bytes(build_pdf([text]))
    assert jd.document.format.value == "pdf"
    assert any("Python" in r.technologies for r in jd.requirements)
