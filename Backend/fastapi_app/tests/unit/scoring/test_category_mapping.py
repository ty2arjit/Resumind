from app.models.enums import RequirementType
from app.modules.scoring.category_mapping import category_for_type
from app.modules.scoring.schemas import ScoringCategory


def test_every_requirement_type_maps_to_exactly_one_category():
    for req_type in RequirementType:
        category = category_for_type(req_type)
        assert isinstance(category, ScoringCategory)


def test_skill_and_preferred_skill_map_to_different_categories():
    assert category_for_type(RequirementType.SKILL) == ScoringCategory.REQUIRED_SKILLS
    assert category_for_type(RequirementType.PREFERRED_SKILL) == ScoringCategory.PREFERRED_SKILLS
