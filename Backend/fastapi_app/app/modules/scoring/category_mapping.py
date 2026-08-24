"""Maps a Phase 3 RequirementType to exactly one ScoringCategory (spec
§13: "each requirement must belong to exactly one primary scoring
category... avoid double counting"). Reuses Phase 3's own classification
rather than re-deriving it.
"""

from app.models.enums import RequirementType
from app.modules.scoring.schemas import ScoringCategory

_TYPE_TO_CATEGORY = {
    RequirementType.SKILL: ScoringCategory.REQUIRED_SKILLS,
    RequirementType.PREFERRED_SKILL: ScoringCategory.PREFERRED_SKILLS,
    RequirementType.RESPONSIBILITY: ScoringCategory.RESPONSIBILITIES,
    RequirementType.EXPERIENCE: ScoringCategory.EXPERIENCE,
    RequirementType.QUALIFICATION: ScoringCategory.QUALIFICATIONS,
    RequirementType.DOMAIN_KNOWLEDGE: ScoringCategory.DOMAIN_KNOWLEDGE,
    RequirementType.OTHER: ScoringCategory.OTHER,
}


def category_for_type(requirement_type: RequirementType) -> ScoringCategory:
    return _TYPE_TO_CATEGORY[requirement_type]
