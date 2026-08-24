from app.modules.resume.schemas import CanonicalSection
from app.modules.resume.sections import detect_sections, leading_content_lines, section_content_lines

SAMPLE = """Jane Smith
jane@example.com

WORK EXPERIENCE
Did some work.

PROJECTS
Built a thing.

TECHNICAL SKILLS
Python, FastAPI
"""


def test_detects_known_sections_with_high_confidence():
    sections = detect_sections(SAMPLE)
    types = [s.canonical_type for s in sections]
    assert CanonicalSection.EXPERIENCE in types
    assert CanonicalSection.PROJECTS in types
    assert CanonicalSection.SKILLS in types
    for s in sections:
        assert s.confidence >= 0.9


def test_heading_variants_normalize_to_canonical_types():
    variants = {
        "Professional Experience": CanonicalSection.EXPERIENCE,
        "Work experience:": CanonicalSection.EXPERIENCE,
        "Academic Projects": CanonicalSection.PROJECTS,
        "Technical Skills": CanonicalSection.SKILLS,
        "Internships": CanonicalSection.EXPERIENCE,
        "Positions of Responsibility": CanonicalSection.LEADERSHIP,
    }
    for heading, expected in variants.items():
        text = f"{heading}\nSome content line."
        sections = detect_sections(text)
        assert sections, f"no section detected for {heading!r}"
        assert sections[0].canonical_type == expected


def test_leading_lines_are_the_header_block():
    sections = detect_sections(SAMPLE)
    leading = leading_content_lines(SAMPLE, sections)
    assert leading == ["Jane Smith", "jane@example.com"]


def test_section_content_lines_excludes_heading_itself():
    sections = detect_sections(SAMPLE)
    experience_section = next(s for s in sections if s.canonical_type == CanonicalSection.EXPERIENCE)
    content = section_content_lines(SAMPLE, experience_section)
    assert "WORK EXPERIENCE" not in content
    assert "Did some work." in content


def test_does_not_assume_every_section_present():
    text = "Jane Smith\n\nSKILLS\nPython, FastAPI\n"
    sections = detect_sections(text)
    types = {s.canonical_type for s in sections}
    assert CanonicalSection.SKILLS in types
    assert CanonicalSection.EXPERIENCE not in types
    assert CanonicalSection.PROJECTS not in types


def test_does_not_treat_data_lines_as_headings():
    """Regression: lines like 'CGPA: 9.23/10' or 'Role, Company' must not
    be misdetected as section headings — they contain digits/commas."""
    text = "EDUCATION\nCGPA: 9.23/10\nEXPERIENCE\nBackend Intern, Example Co\nDid stuff."
    sections = detect_sections(text)
    headings = [s.heading_text for s in sections]
    assert "CGPA: 9.23/10" not in headings
    assert "Backend Intern, Example Co" not in headings
