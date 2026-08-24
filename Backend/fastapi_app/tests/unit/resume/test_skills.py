from app.modules.resume.skills import parse_skills_section


def test_categorized_skills_by_labeled_lines():
    lines = ["Languages: Python, Java, C++", "Frameworks: React, Node.js"]
    categories = parse_skills_section(lines)
    by_category = {c.category: c.items for c in categories}
    assert by_category["programming_languages"] == ["Python", "Java", "C++"]
    assert by_category["frameworks"] == ["React", "Node.js"]


def test_unlabeled_line_goes_to_other():
    lines = ["Python, FastAPI, PostgreSQL"]
    categories = parse_skills_section(lines)
    assert len(categories) == 1
    assert categories[0].category == "other"
    assert categories[0].items == ["Python", "FastAPI", "PostgreSQL"]


def test_unknown_label_preserved_as_raw_category_label():
    lines = ["Soft Skills: Communication, Leadership"]
    categories = parse_skills_section(lines)
    assert categories[0].category == "other"
    assert categories[0].category_label == "Soft Skills"


def test_deduplicates_items_within_a_category():
    lines = ["Languages: Python, Python, Java"]
    categories = parse_skills_section(lines)
    assert categories[0].items == ["Python", "Java"]


def test_empty_section_returns_no_categories():
    assert parse_skills_section([]) == []
