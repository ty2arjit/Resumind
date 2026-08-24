from app.modules.resume.actions import extract_actions, leading_action


def test_extracts_leading_action_verb():
    assert leading_action("Built REST APIs using FastAPI") == "Built"


def test_extracts_multiple_actions_in_order():
    actions = extract_actions("Designed and Implemented a caching layer")
    assert actions == ["Designed", "Implemented"]


def test_no_action_verb_present():
    assert leading_action("Responsible for various tasks around the office") is None


def test_case_insensitive_but_preserves_original_casing():
    assert extract_actions("built a small tool") == ["built"]


def test_vocabulary_is_data_driven():
    """The action vocabulary must come from the configurable data file, not
    be hardcoded in the module itself (spec §12)."""
    from app.modules.resume.vocab import get_action_verbs

    verbs = get_action_verbs()
    assert "Built" in verbs
    assert len(verbs) > 10
