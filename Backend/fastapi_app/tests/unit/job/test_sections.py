from app.modules.job.schemas import JDCanonicalSection
from app.modules.job.sections import detect_sections, leading_content_lines, section_content_lines

SAMPLE = """Backend Software Engineer

RESPONSIBILITIES
Design scalable backend services.

REQUIRED QUALIFICATIONS
Strong experience with Python.

PREFERRED QUALIFICATIONS
Experience with AWS.
"""


def test_detects_known_sections_with_high_confidence():
    sections = detect_sections(SAMPLE)
    types = [s.canonical_type for s in sections]
    assert JDCanonicalSection.RESPONSIBILITIES in types
    assert JDCanonicalSection.QUALIFICATIONS_REQUIRED in types
    assert JDCanonicalSection.QUALIFICATIONS_PREFERRED in types
    for s in sections:
        assert s.confidence >= 0.9


def test_heading_variants_normalize_to_canonical_types():
    variants = {
        "Key Responsibilities": JDCanonicalSection.RESPONSIBILITIES,
        "What You'll Do": JDCanonicalSection.RESPONSIBILITIES,
        "Required Qualifications": JDCanonicalSection.QUALIFICATIONS_REQUIRED,
        "Must Have": JDCanonicalSection.QUALIFICATIONS_REQUIRED,
        "Preferred Qualifications": JDCanonicalSection.QUALIFICATIONS_PREFERRED,
        "Nice to Have": JDCanonicalSection.QUALIFICATIONS_PREFERRED,
        "Technical Skills": JDCanonicalSection.SKILLS,
        "About the Company": JDCanonicalSection.ABOUT_COMPANY,
    }
    for heading, expected in variants.items():
        text = f"{heading}\nSome content line."
        sections = detect_sections(text)
        assert sections, f"no section detected for {heading!r}"
        assert sections[0].canonical_type == expected


def test_title_line_is_not_swallowed_as_a_section():
    """Regression: line 0 (the job title) must not be treated as a
    section heading, or leading_content_lines() (used by metadata
    extraction) breaks."""
    sections = detect_sections(SAMPLE)
    leading = leading_content_lines(SAMPLE, sections)
    assert leading == ["Backend Software Engineer"]


def test_label_value_lines_are_not_treated_as_headings():
    """Regression: 'Company: Example Corp' structurally resembles a
    heading (Title Case, short) but is a label/value line."""
    text = "Backend Engineer\nCompany: Example Corp\nLocation: Bengaluru\n\nRESPONSIBILITIES\nBuild things.\n"
    sections = detect_sections(text)
    headings = [s.heading_text for s in sections]
    assert "Company: Example Corp" not in headings
    assert "Location: Bengaluru" not in headings


def test_section_content_lines_excludes_heading_itself():
    sections = detect_sections(SAMPLE)
    resp_section = next(s for s in sections if s.canonical_type == JDCanonicalSection.RESPONSIBILITIES)
    content = section_content_lines(SAMPLE, resp_section)
    assert "RESPONSIBILITIES" not in content
    assert "Design scalable backend services." in content


def test_does_not_assume_every_section_present():
    text = "Backend Engineer\n\nSKILLS\nPython, FastAPI\n"
    sections = detect_sections(text)
    types = {s.canonical_type for s in sections}
    assert JDCanonicalSection.SKILLS in types
    assert JDCanonicalSection.RESPONSIBILITIES not in types
