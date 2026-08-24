from app.modules.resume.clean import clean_text


def test_collapses_excessive_blank_lines():
    raw = "A\n\n\n\n\nB"
    assert clean_text(raw) == "A\n\nB"


def test_collapses_repeated_spaces():
    raw = "Python    Developer"
    assert clean_text(raw) == "Python Developer"


def test_dehyphenates_line_wrap_artifacts():
    raw = "Built a scalable applica-\ntion using FastAPI"
    assert "application using FastAPI" in clean_text(raw)


def test_removes_page_number_only_lines():
    raw = "Experience\nDetails here\n3\nMore details"
    cleaned = clean_text(raw)
    assert "\n3\n" not in f"\n{cleaned}\n"


def test_removes_repeated_header_footer_across_pages():
    pages = ["John Doe Resume\nPage content one\nJohn Doe Resume", "John Doe Resume\nPage content two\nJohn Doe Resume"]
    raw = "\n\f\n".join(pages)
    cleaned = clean_text(raw, pages)
    assert cleaned.count("John Doe Resume") <= 1


def test_collapses_adjacent_duplicate_lines():
    raw = "Built REST APIs using FastAPI and PostgreSQL\nBuilt REST APIs using FastAPI and PostgreSQL"
    cleaned = clean_text(raw)
    assert cleaned.count("Built REST APIs using FastAPI and PostgreSQL") == 1


def test_raw_text_is_never_mutated_by_caller_expectations():
    raw = "  messy   text  "
    cleaned = clean_text(raw)
    assert cleaned != raw  # cleaning did something
    assert raw == "  messy   text  "  # but the caller's original string is untouched
