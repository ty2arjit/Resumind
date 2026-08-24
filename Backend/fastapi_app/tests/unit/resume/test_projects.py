from app.modules.resume.projects import parse_projects_section


def test_project_with_tech_stack_header_and_bullets():
    lines = [
        "Resumind | React, FastAPI, PostgreSQL",
        "An AI-powered resume analyzer.",
        "- Implemented resume parsing pipeline handling 50+ resumes.",
        "- Integrated PostgreSQL for structured storage.",
    ]
    entries, evidence = parse_projects_section(lines)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.name == "Resumind"
    assert entry.description == "An AI-powered resume analyzer."
    assert len(entry.bullets) == 2
    assert "FastAPI" in entry.technologies
    assert "PostgreSQL" in entry.technologies
    assert len(evidence) == 2


def test_extracts_project_links():
    lines = ["My App", "Live at https://myapp.example.com and code at https://github.com/me/myapp"]
    entries, _ = parse_projects_section(lines)
    assert any("myapp.example.com" in link for link in entries[0].links)


def test_multiple_projects():
    lines = [
        "Project One",
        "- Did something.",
        "Project Two",
        "- Did something else.",
    ]
    entries, _ = parse_projects_section(lines)
    assert len(entries) == 2
    assert entries[0].name == "Project One"
    assert entries[1].name == "Project Two"


def test_project_without_description_line():
    lines = ["Simple Project", "- Just one bullet."]
    entries, _ = parse_projects_section(lines)
    assert entries[0].description is None
    assert entries[0].bullets == ["Just one bullet."]


def test_empty_section_returns_no_entries():
    entries, evidence = parse_projects_section([])
    assert entries == []
    assert evidence == []
