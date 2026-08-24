from app.modules.matching.experience import match_experience
from app.modules.resume.schemas import DateRange, ExperienceEntry


def _entry(months, technologies):
    return ExperienceEntry(
        organization="Example Co",
        role="Backend Engineer",
        dates=DateRange(duration_months=months),
        technologies=technologies,
        raw_header="x",
    )


def test_sufficient_relevant_experience():
    result = match_experience(3.0, ["Python"], "Python development", [_entry(36, ["Python"])])
    assert result.detected_years == 3.0
    assert result.confidence > 0.8


def test_no_requirement_returns_zero_confidence():
    result = match_experience(None, [], None, [])
    assert result.confidence == 0.0
    assert result.detected_years is None


def test_unreliable_dates_do_not_fabricate_a_duration():
    entry = ExperienceEntry(organization="Co", role="Engineer", dates=None, technologies=["Python"], raw_header="x")
    result = match_experience(3.0, ["Python"], "Python", [entry])
    assert result.detected_years is None
    assert result.required_years == 3.0


def test_irrelevant_experience_is_excluded():
    """Experience in an unrelated technology must not count toward a
    specific technology's experience requirement."""
    result = match_experience(3.0, ["Kubernetes"], "Kubernetes", [_entry(36, ["Python"])])
    assert result.detected_years is None


def test_multiple_relevant_entries_are_summed():
    entries = [_entry(12, ["Python"]), _entry(24, ["Python"])]
    result = match_experience(2.0, ["Python"], "Python", entries)
    assert result.detected_years == 3.0
