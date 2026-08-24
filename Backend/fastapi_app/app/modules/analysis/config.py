"""Centralized, versioned Analysis Engine configuration (spec Phase 10
§5, §10, §16). This module never recalculates ATS/Target Fit/Resume
Quality scores — these values only rank/bucket the already-computed
per-requirement fields (importance, weight, category.normalized_weight,
status) into strength/gap priorities.
"""

from functools import lru_cache

from pydantic import BaseModel


class AnalysisLimits(BaseModel):
    """spec §5, §16 — do not overwhelm the candidate."""

    top_n_strengths: int = 5
    top_n_recommendations: int = 5


class GapPriorityThresholds(BaseModel):
    """spec §10 — impact_score = importance_weight * category_normalized_weight
    * requirement_weight, a relative (not point-value) ranking signal
    derived purely from already-computed Phase 3/7 fields."""

    critical_impact: float = 0.12
    high_impact: float = 0.06
    medium_impact: float = 0.02


class ImportanceWeightMap(BaseModel):
    required: float = 1.0
    preferred: float = 0.6
    optional: float = 0.3
    unknown: float = 0.5

    def for_importance(self, importance: str) -> float:
        return {
            "REQUIRED": self.required,
            "PREFERRED": self.preferred,
            "OPTIONAL": self.optional,
            "UNKNOWN": self.unknown,
        }.get(importance, self.unknown)


class StrengthThresholds(BaseModel):
    """spec §4 — which matches are strong enough to surface as a
    strength at all, before top-N prioritization trims the list."""

    minimum_status_rank: int = 3  # STRONG=3, VERY_STRONG=4 in _STATUS_RANK
    high_quality_dimension_threshold: float = 0.85
    strong_fit_threshold: int = 75


#: Bumped when the strength/gap/recommendation derivation rules change
#: shape, independent of AnalysisConfig.version (numeric-only retuning).
ALGORITHM_VERSION = "ANALYSIS_ENGINE_V1"


class AnalysisConfig(BaseModel):
    version: str = "ANALYSIS_CONFIG_V1"
    limits: AnalysisLimits = AnalysisLimits()
    gap_priority_thresholds: GapPriorityThresholds = GapPriorityThresholds()
    importance_weights: ImportanceWeightMap = ImportanceWeightMap()
    strength_thresholds: StrengthThresholds = StrengthThresholds()


@lru_cache
def get_analysis_config() -> AnalysisConfig:
    return AnalysisConfig()
