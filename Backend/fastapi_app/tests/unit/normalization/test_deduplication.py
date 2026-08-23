from app.modules.normalization.entities import normalize_skill
from app.modules.normalization.service import group_by_canonical


def test_python_variants_group_under_the_same_canonical():
    """spec §9: Python / Python3 / Python 3.x refer to the same skill —
    raw mentions must still be individually preserved in the group."""
    entities = [normalize_skill(v) for v in ("Python", "Python3", "Python 3.x")]
    groups = group_by_canonical(entities)

    assert list(groups.keys()) == ["Python"]
    raw_mentions = [e.raw_value for e in groups["Python"]]
    assert raw_mentions == ["Python", "Python3", "Python 3.x"]


def test_distinct_skills_form_separate_groups():
    entities = [normalize_skill(v) for v in ("Python", "Java", "Docker")]
    groups = group_by_canonical(entities)
    assert set(groups.keys()) == {"Python", "Java", "Docker"}


def test_unknown_entities_are_grouped_by_raw_value_not_dropped():
    entities = [normalize_skill("SomeUnknownThing")]
    groups = group_by_canonical(entities)
    assert groups == {"SomeUnknownThing": entities}
