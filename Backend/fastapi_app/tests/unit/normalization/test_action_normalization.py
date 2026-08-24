from app.modules.normalization.actions import normalize_action
from app.modules.normalization.schemas import NormalizationStatus


def test_built_and_build_map_to_same_canonical():
    assert normalize_action("Built").canonical_action == normalize_action("Build").canonical_action


def test_developed_and_develop_map_to_same_canonical():
    assert normalize_action("Developed").canonical_action == normalize_action("Develop").canonical_action


def test_build_and_develop_are_distinct_canonicals():
    """spec §15 groups these as related but the taxonomy keeps each verb's
    own canonical rather than merging unrelated concepts."""
    assert normalize_action("Build").canonical_action != normalize_action("Develop").canonical_action


def test_reuses_shared_action_vocabulary():
    """The recognized raw forms must be exactly the resume/JD parsers'
    own vocabulary — not a second, separately maintained list."""
    from app.modules.resume.vocab import get_action_verbs

    for verb in get_action_verbs():
        assert normalize_action(verb).canonical_action is not None, f"{verb!r} not covered by action normalization"


def test_unrecognized_action_is_unknown():
    r = normalize_action("Vibed")
    assert r.canonical_action is None
    assert r.normalization_status == NormalizationStatus.UNKNOWN
