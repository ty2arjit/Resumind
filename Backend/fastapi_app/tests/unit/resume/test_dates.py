from app.modules.resume.dates import extract_date_range


def test_month_year_range():
    dr = extract_date_range("Jan 2024 - Mar 2025")
    assert dr.start_normalized == "2024-01"
    assert dr.end_normalized == "2025-03"
    assert dr.duration_months == 14
    assert not dr.is_current


def test_full_month_name():
    dr = extract_date_range("January 2024 - March 2025")
    assert dr.start_normalized == "2024-01"
    assert dr.end_normalized == "2025-03"


def test_numeric_month_format():
    dr = extract_date_range("01/2024 - 03/2025")
    assert dr.start_normalized == "2024-01"
    assert dr.end_normalized == "2025-03"


def test_year_only_range():
    dr = extract_date_range("2020 - 2024")
    assert dr.start_normalized == "2020"
    assert dr.end_normalized == "2024"
    assert dr.duration_months is None  # too imprecise to report months


def test_present_is_treated_as_current():
    dr = extract_date_range("Jun 2023 - Present")
    assert dr.start_normalized == "2023-06"
    assert dr.end_normalized is None
    assert dr.is_current is True
    assert dr.end_text == "Present"


def test_current_keyword_variants():
    for word in ("Current", "Ongoing", "Present"):
        dr = extract_date_range(f"2022 - {word}")
        assert dr.is_current is True


def test_no_date_present_returns_none():
    assert extract_date_range("Improved code quality across the team") is None


def test_malformed_date_does_not_fabricate_normalized_value():
    dr = extract_date_range("Sometime in twenty twenty-four")
    assert dr is None


def test_does_not_double_count_year_inside_month_year():
    """Regression: 'Jun 2023 - Aug 2023' must not let the standalone-year
    regex match '2023' from inside 'Aug 2023' and corrupt the end date."""
    dr = extract_date_range("Jun 2023 - Aug 2023")
    assert dr.start_text == "Jun 2023"
    assert dr.end_text == "Aug 2023"
    assert dr.duration_months == 2
