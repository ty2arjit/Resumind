from app.modules.matching.qualification import match_qualification
from app.modules.resume.schemas import EducationEntry


def _entry(degree, field):
    return EducationEntry(institution="NIT Rourkela", degree=degree, field=field, raw_text="x")


def test_exact_degree_and_field_match():
    result = match_qualification("Bachelor's", "Computer Science", [_entry("B.Tech", "Computer Science")])
    assert result.matched is True
    assert result.uncertain is False


def test_or_related_field_is_permissive():
    result = match_qualification("Bachelor's", "Computer Science or related field", [_entry("B.Tech", "Information Technology")])
    assert result.matched is True


def test_unrelated_field_is_not_automatically_equivalent():
    result = match_qualification("Bachelor's", "Computer Science", [_entry("B.Tech", "Biotechnology")])
    assert result.matched is False


def test_no_education_returns_uncertain():
    result = match_qualification("Bachelor's", "Computer Science", [])
    assert result.matched is False
    assert result.uncertain is True
    assert result.confidence == 0.0


def test_degree_level_only_requirement():
    """Requirement doesn't specify a field — any Bachelor's-level degree
    should satisfy the degree-level check."""
    result = match_qualification("Bachelor's", None, [_entry("B.Tech", "Mechanical Engineering")])
    assert result.matched is True
