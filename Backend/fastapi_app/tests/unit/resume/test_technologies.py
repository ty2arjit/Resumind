from app.modules.resume.technologies import extract_technologies


def test_detects_common_technologies():
    techs = extract_technologies("Built with Python, FastAPI and PostgreSQL")
    assert "Python" in techs
    assert "FastAPI" in techs
    assert "PostgreSQL" in techs


def test_does_not_normalize_variants():
    """Spec §14: React.js / ReactJS / React must remain distinct raw
    mentions in this phase — normalization is Phase 4."""
    techs = extract_technologies("Used React.js on one project and plain React on another")
    assert "React.js" in techs
    assert "React" in techs


def test_longer_terms_win_over_substrings():
    techs = extract_technologies("Deployed with Node.js and Express.js")
    assert "Node.js" in techs
    assert "Express.js" in techs
    assert "Node" not in techs  # "Node" alone isn't in the vocabulary, only "Node.js"


def test_no_technology_mentions():
    assert extract_technologies("Led a team of five people") == []


def test_deduplicates_repeated_mentions():
    techs = extract_technologies("Python Python Python")
    assert techs == ["Python"]
