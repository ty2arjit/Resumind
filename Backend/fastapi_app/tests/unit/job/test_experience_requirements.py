from app.modules.job.experience_requirements import extract_experience_requirement


def test_plus_years():
    req = extract_experience_requirement("2+ years of Python development")
    assert req.min_years == 2.0
    assert req.max_years is None
    assert req.context == "Python development"


def test_range_years():
    req = extract_experience_requirement("3-5 years of backend engineering")
    assert req.min_years == 3.0
    assert req.max_years == 5.0
    assert req.context == "backend engineering"


def test_at_least_years():
    req = extract_experience_requirement("At least 1 year of experience with AWS")
    assert req.min_years == 1.0
    assert req.max_years is None
    assert req.context == "AWS"


def test_minimum_of_years():
    req = extract_experience_requirement("Minimum of 2 years in software development")
    assert req.min_years == 2.0


def test_no_years_mentioned_returns_none():
    assert extract_experience_requirement("Strong Python skills") is None


def test_does_not_infer_from_unrelated_numbers():
    """Spec §10: only explicit '<N> years' phrasing counts — a stray
    number must not be misread as an experience requirement."""
    assert extract_experience_requirement("Team of 5 engineers") is None
