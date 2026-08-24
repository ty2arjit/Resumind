from app.modules.resume.education import parse_education_section


def test_extracts_institution_degree_field_and_gpa():
    lines = ["NIT Rourkela", "B.Tech in Biotechnology, 2020 - 2024", "CGPA: 9.23/10"]
    entries = parse_education_section(lines)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.institution == "NIT Rourkela"
    assert entry.degree is not None and "tech" in entry.degree.lower()
    assert entry.field == "Biotechnology"
    assert entry.gpa == "9.23"
    assert entry.dates.start_normalized == "2020"
    assert entry.dates.end_normalized == "2024"


def test_extracts_percentage_when_present_instead_of_gpa():
    lines = ["ABC High School", "Higher Secondary, 2018", "Percentage: 92.5%"]
    entries = parse_education_section(lines)
    assert entries[0].percentage == "92.5%"


def test_multiple_education_entries():
    lines = [
        "NIT Rourkela",
        "B.Tech in Computer Science, 2020 - 2024",
        "ABC Public School",
        "12th Grade, 2020",
    ]
    entries = parse_education_section(lines)
    assert len(entries) == 2
    assert entries[0].institution == "NIT Rourkela"
    assert entries[1].institution == "ABC Public School"


def test_does_not_invent_missing_fields():
    entries = parse_education_section(["Some College"])
    assert entries[0].institution == "Some College"
    assert entries[0].gpa is None
    assert entries[0].degree is None


def test_empty_section_returns_no_entries():
    assert parse_education_section([]) == []
