"""Builds target-profile requirements compatible with the existing
Requirement structure (spec §12) so Phase 5's Matching Engine and Phase
6's Evidence Engine can be reused verbatim — no second matching system.
"""

from app.models.enums import ImportanceLevel, RequirementType
from app.modules.job.schemas import Requirement
from app.modules.target_profile.config import TargetRequirementWeights
from app.modules.target_profile.schemas import TargetProfileCategories

#: (profile field, id slug, RequirementType, importance, weight attr,
#: whether the raw text is itself a technology entity for exact/canonical
#: matching)
_CATEGORY_SPECS = [
    ("core_skills", "core", RequirementType.SKILL, ImportanceLevel.REQUIRED, "core_skills", True),
    ("technologies", "tech", RequirementType.SKILL, ImportanceLevel.REQUIRED, "technologies", True),
    ("responsibilities", "resp", RequirementType.RESPONSIBILITY, ImportanceLevel.REQUIRED, "responsibilities", False),
    ("experience_expectations", "exp", RequirementType.EXPERIENCE, ImportanceLevel.REQUIRED, "experience", False),
    ("domain_knowledge", "domain", RequirementType.DOMAIN_KNOWLEDGE, ImportanceLevel.REQUIRED, "domain_knowledge", False),
    ("preferred_skills", "pref", RequirementType.PREFERRED_SKILL, ImportanceLevel.PREFERRED, "preferred_skills", True),
]


def build_target_requirements(
    categories: TargetProfileCategories, weights: TargetRequirementWeights
) -> list[Requirement]:
    requirements: list[Requirement] = []

    for field_name, id_slug, req_type, importance, weight_attr, is_technology in _CATEGORY_SPECS:
        items = getattr(categories, field_name)
        weight = getattr(weights, weight_attr)
        for index, item in enumerate(items):
            requirements.append(
                Requirement(
                    id=f"tgt_{id_slug}_{index}",
                    text=item,
                    type=req_type,
                    importance=importance,
                    weight=weight,
                    critical=False,
                    confidence=1.0,
                    technologies=[item] if is_technology else [],
                )
            )

    return requirements
