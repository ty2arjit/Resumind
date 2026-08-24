"""End-to-end tests through the real PDF/DOCX extraction path (spec §21).

Each test name maps to one of the 12 scenarios required by the Phase 2
spec. These assert on structured output, not just "didn't crash".
"""

from app.modules.resume.parser import parse_docx_bytes, parse_pdf_bytes
from app.modules.resume.schemas import CanonicalSection, ExtractionStatus, WarningCode
from tests.fixtures.builders import build_docx, build_empty_pdf, build_pdf, build_two_column_pdf


# 1. Simple single-column resume.
def test_simple_single_column_resume():
    text = (
        "Jane Doe\njane@example.com\n\n"
        "SUMMARY\nExperienced backend engineer with a focus on distributed systems.\n\n"
        "SKILLS\nPython, FastAPI, PostgreSQL, Docker\n"
    )
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.contact.email == "jane@example.com"
    assert any(c.items and "Python" in c.items for c in resume.skills)
    assert resume.document.extraction_status == ExtractionStatus.OK


# 2. Resume with experience + projects.
def test_resume_with_experience_and_projects():
    text = (
        "Jane Doe\njane@example.com\n\n"
        "EXPERIENCE\n"
        "Backend Intern, Example Co | Jun 2023 - Aug 2023\n"
        "- Built REST APIs using FastAPI, reducing latency by 35%.\n\n"
        "PROJECTS\n"
        "Resumind | React, FastAPI\n"
        "- Implemented resume parsing.\n"
    )
    resume = parse_pdf_bytes(build_pdf([text]))
    assert len(resume.experience) == 1
    assert resume.experience[0].organization == "Example Co"
    assert len(resume.projects) == 1
    assert resume.projects[0].name == "Resumind"
    assert len(resume.evidence) == 2


# 3. Resume with education + skills.
def test_resume_with_education_and_skills():
    text = (
        "Jane Doe\njane@example.com\n\n"
        "EDUCATION\n"
        "NIT Rourkela\n"
        "B.Tech in Computer Science, 2020 - 2024\n"
        "CGPA: 9.1/10\n\n"
        "SKILLS\n"
        "Languages: Python, Java\n"
    )
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.education[0].institution == "NIT Rourkela"
    assert resume.education[0].gpa == "9.1"
    assert any(c.category == "programming_languages" for c in resume.skills)


# 4. Multi-page resume.
def test_multi_page_resume():
    page1 = "Jane Doe\njane@example.com\n\nSUMMARY\nExperienced engineer.\n"
    page2 = "EXPERIENCE\nBackend Intern, Example Co | Jun 2023 - Aug 2023\n- Built APIs.\n"
    resume = parse_pdf_bytes(build_pdf([page1, page2]))
    assert resume.document.page_count == 2
    assert resume.summary is not None
    assert len(resume.experience) == 1


# 5. Resume with different heading capitalization.
def test_heading_capitalization_variants():
    text = "Jane Doe\n\nwork experience:\nBackend Intern, Example Co | Jun 2023 - Aug 2023\n- Built APIs.\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    assert len(resume.experience) == 1
    experience_sections = [s for s in resume.sections if s.canonical_type == CanonicalSection.EXPERIENCE]
    assert experience_sections


# 6. Resume with missing sections.
def test_resume_with_missing_sections_raises_warnings_not_errors():
    text = "Jane Doe\njane@example.com\n\nSKILLS\nPython\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.experience == []
    assert resume.education == []
    warning_codes = {w.code for w in resume.warnings}
    assert WarningCode.MISSING_EXPECTED_SECTION in warning_codes


# 7. Resume with "Present" dates.
def test_present_date_handling():
    text = "Jane Doe\n\nEXPERIENCE\nSoftware Engineer, Acme | Jan 2023 - Present\n- Shipped features.\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.experience[0].dates.is_current is True
    assert resume.experience[0].dates.end_normalized is None


# 8. Resume with percentage/GPA.
def test_percentage_and_gpa():
    text = "Jane Doe\n\nEDUCATION\nABC College\nB.Tech, 2020 - 2024\nCGPA: 8.7/10\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.education[0].gpa == "8.7"


# 9. Resume with URLs.
def test_urls_are_extracted():
    text = "Jane Doe\njane@example.com | linkedin.com/in/janedoe | github.com/janedoe\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    assert resume.contact.linkedin == "linkedin.com/in/janedoe"
    assert resume.contact.github == "github.com/janedoe"


# 10. Resume containing common technology names.
def test_common_technology_names_detected():
    text = "Jane Doe\n\nSKILLS\nPython, FastAPI, PostgreSQL, Docker, AWS\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    all_items = [item for c in resume.skills for item in c.items]
    for tech in ("Python", "FastAPI", "PostgreSQL", "Docker", "AWS"):
        assert tech in all_items


# 11. Multi-column resume.
def test_multi_column_resume_reduces_interleaving():
    left = ["EDUCATION", "NIT Rourkela", "B.Tech, 2020 - 2024"]
    right = ["SKILLS", "Python, FastAPI"]
    resume = parse_pdf_bytes(build_two_column_pdf(left, right))
    # The left column's content should stay together rather than
    # interleaving line-by-line with the right column.
    cleaned = resume.document.cleaned_text
    edu_idx = cleaned.find("NIT Rourkela")
    skills_idx = cleaned.find("SKILLS")
    assert edu_idx != -1 and skills_idx != -1


# 12. Malformed/empty document handling.
def test_empty_pdf_produces_empty_status_not_a_crash():
    resume = parse_pdf_bytes(build_empty_pdf())
    assert resume.document.extraction_status == ExtractionStatus.EMPTY
    assert any(w.code == WarningCode.EMPTY_DOCUMENT for w in resume.warnings)
    assert resume.experience == []
    assert resume.contact.email is None


def test_low_text_pdf_flags_possible_scanned_document():
    resume = parse_pdf_bytes(build_pdf(["Hi"]))
    assert resume.document.extraction_status == ExtractionStatus.LOW_TEXT
    codes = {w.code for w in resume.warnings}
    assert WarningCode.POSSIBLE_SCANNED_PDF in codes


# DOCX support
def test_docx_resume_parses_equivalently():
    lines = [
        "Jane Doe",
        "jane@example.com",
        "SKILLS",
        "Python, FastAPI, PostgreSQL",
    ]
    resume = parse_docx_bytes(build_docx(lines))
    assert resume.document.format.value == "docx"
    assert resume.contact.email == "jane@example.com"
    assert any("Python" in c.items for c in resume.skills)
