from app.modules.resume.experience import parse_experience_section


def test_inline_header_with_role_and_organization():
    lines = [
        "Backend Developer Intern, Example Company | Jun 2023 - Aug 2023",
        "- Built REST APIs using FastAPI and PostgreSQL, reducing response latency by 35%.",
        "- Deployed services on AWS using Docker and Kubernetes.",
    ]
    entries, evidence, warnings = parse_experience_section(lines)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.role == "Backend Developer Intern"
    assert entry.organization == "Example Company"
    assert entry.dates.start_normalized == "2023-06"
    assert entry.dates.end_normalized == "2023-08"
    assert len(entry.bullets) == 2
    assert "FastAPI" in entry.technologies
    assert len(evidence) == 2


def test_two_line_header_role_then_dates():
    """Common real-world layout: role/org on one line, the date range
    alone on the next."""
    lines = [
        "Backend Developer Intern, Example Company",
        "Jun 2023 - Aug 2023",
        "- Built REST APIs using FastAPI.",
    ]
    entries, evidence, warnings = parse_experience_section(lines)
    assert len(entries) == 1
    assert entries[0].role == "Backend Developer Intern"
    assert entries[0].organization == "Example Company"
    assert entries[0].bullets == ["Built REST APIs using FastAPI."]


def test_present_marks_entry_as_current():
    lines = ["Software Engineer, Acme Corp | Jan 2023 - Present", "- Shipped features."]
    entries, _, _ = parse_experience_section(lines)
    assert entries[0].dates.is_current is True


def test_ambiguous_header_preserves_raw_text_and_warns():
    lines = ["Some Freeform Header With No Delimiter 2022 - 2023", "- Did things."]
    entries, _, warnings = parse_experience_section(lines)
    assert entries[0].raw_header
    assert len(warnings) == 1


def test_multiple_experience_entries():
    lines = [
        "Role A, Company A | Jan 2022 - Dec 2022",
        "- Did A.",
        "Role B, Company B | Jan 2023 - Present",
        "- Did B.",
    ]
    entries, _, _ = parse_experience_section(lines)
    assert len(entries) == 2
    assert entries[0].organization == "Company A"
    assert entries[1].organization == "Company B"


def test_empty_section_returns_no_entries():
    entries, evidence, warnings = parse_experience_section([])
    assert entries == []
    assert evidence == []
