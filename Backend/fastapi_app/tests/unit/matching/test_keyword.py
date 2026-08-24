from app.modules.matching.keyword import keyword_signal


def test_full_overlap():
    signal, overlap = keyword_signal("PostgreSQL", "PostgreSQL")
    assert signal == 1.0


def test_java_does_not_match_inside_javascript():
    """Regression: word-boundary tokenization must prevent 'Java' from
    matching as a substring of 'JavaScript'."""
    signal, overlap = keyword_signal("Java", "Built frontend apps using JavaScript")
    assert signal == 0.0
    assert overlap == []


def test_partial_overlap():
    signal, overlap = keyword_signal("PostgreSQL database", "PostgreSQL")
    assert 0.0 < signal < 1.0
    assert "postgresql" in overlap


def test_no_overlap():
    signal, overlap = keyword_signal("Kubernetes", "Unrelated marketing content")
    assert signal == 0.0


def test_empty_requirement_text():
    signal, overlap = keyword_signal("", "some evidence text")
    assert signal == 0.0
