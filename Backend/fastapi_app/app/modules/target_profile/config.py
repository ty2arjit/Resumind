"""Centralized, versioned Target Profile / Target Fit configuration
(spec Phase 9 §9, §17). Deliberately separate from app.modules.scoring's
ATS weights — "Do not copy the ATS scoring weights blindly. Target
profiles have a different purpose" (spec §17)."""

from functools import lru_cache

from pydantic import BaseModel, field_validator


class TargetRequirementWeights(BaseModel):
    """Per-category weight assigned to generated target requirements —
    analogous to Phase 3's importance weighting, but this engine's own
    values rather than reusing RequirementImportanceWeights."""

    core_skills: float = 1.0
    technologies: float = 0.9
    responsibilities: float = 0.8
    experience: float = 0.9
    domain_knowledge: float = 0.85
    preferred_skills: float = 0.5


class TargetFitDimensionWeights(BaseModel):
    """Spec §13-14, §17 — Position Fit aggregates core skills,
    technologies, responsibilities, and experience evidence; Domain Fit
    aggregates domain-knowledge evidence specifically. Must sum to 1.0."""

    position_fit: float = 0.65
    domain_fit: float = 0.35

    @field_validator("domain_fit")
    @classmethod
    def _weights_sum_to_one(cls, domain_fit: float, info) -> float:
        total = sum(info.data.values()) + domain_fit
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"target fit dimension weights must sum to 1.0, got {total}")
        return domain_fit


#: Bumped when the Target Fit scoring formula's shape changes, independent
#: of TargetProfileConfig.version (numeric-only retuning).
ALGORITHM_VERSION = "TARGET_FIT_V1"

#: Bumped whenever the curated registry content (target_profile_registry.json)
#: changes — independent of the code-level knowledge_version stored inside
#: that file, which tracks the normalization taxonomy it was written against.
PROFILE_VERSION = "TARGET_PROFILE_V1"


class TargetProfileConfig(BaseModel):
    version: str = "TARGET_PROFILE_CONFIG_V1"
    requirement_weights: TargetRequirementWeights = TargetRequirementWeights()
    fit_dimension_weights: TargetFitDimensionWeights = TargetFitDimensionWeights()


@lru_cache
def get_target_profile_config() -> TargetProfileConfig:
    return TargetProfileConfig()
