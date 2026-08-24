"""Centralized, versioned Resume Quality configuration (spec Phase 8 §25,
§27). Deliberately separate from app.modules.scoring.config — Resume
Quality is an independent engine from ATS Alignment (spec §1) and must
never share weights/thresholds with it, even where numbers coincide.

`config_version` bumps whenever these numbers change; `ALGORITHM_VERSION`
bumps when the dimension formulas themselves change shape.
"""

from functools import lru_cache

from pydantic import BaseModel, field_validator


class QualityDimensionWeights(BaseModel):
    """Spec §25 — initial heuristic weights, not scientifically validated.
    Must sum to 1.0."""

    parseability: float = 0.20
    structure: float = 0.15
    content_completeness: float = 0.10
    evidence_quality: float = 0.20
    date_consistency: float = 0.10
    contact_completeness: float = 0.05
    keyword_hygiene: float = 0.05
    section_consistency: float = 0.05
    content_density: float = 0.10

    @field_validator("content_density")
    @classmethod
    def _weights_sum_to_one(cls, content_density: float, info) -> float:
        total = sum(info.data.values()) + content_density
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"quality dimension weights must sum to 1.0, got {total}")
        return content_density


class WarningPenaltyConfig(BaseModel):
    """Spec §6 — warnings influence parseability in a controlled way; no
    single warning may destroy the whole score (max_total_penalty caps
    the cumulative reduction)."""

    weights: dict[str, float] = {
        "empty_document": 0.30,
        "possible_scanned_pdf": 0.20,
        "low_extracted_text": 0.15,
        "unsupported_layout": 0.15,
        "multiple_sections_merged": 0.10,
        "duplicate_content_removed": 0.10,
        "ambiguous_section": 0.08,
        "ambiguous_experience_header": 0.08,
        "ambiguous_education_entry": 0.05,
        "malformed_date": 0.05,
        "missing_expected_section": 0.03,
    }
    default_weight: float = 0.05
    max_total_penalty: float = 0.50


class ParseabilityConfig(BaseModel):
    ok_score: float = 1.0
    low_text_score: float = 0.5
    empty_score: float = 0.0
    target_section_count: int = 4
    warning_penalty: WarningPenaltyConfig = WarningPenaltyConfig()


class StructureConfig(BaseModel):
    target_section_breadth: int = 3
    no_content_coherence_score: float = 0.6


class SectionConsistencyConfig(BaseModel):
    inconsistency_ratio_finding_threshold: float = 0.6
    no_entries_default_score: float = 0.8


class ContentCompletenessConfig(BaseModel):
    total_category_count: int = 6


class EvidenceQualityConfig(BaseModel):
    no_evidence_score: float = 0.4
    low_metric_ratio_threshold: float = 0.20
    low_action_ratio_threshold: float = 0.50


class DateConsistencyConfig(BaseModel):
    no_dates_default_score: float = 0.8
    unparseable_date_penalty: float = 0.5
    invalid_order_penalty: float = 0.5


class ContactCompletenessConfig(BaseModel):
    core_weight: float = 0.70
    optional_weight: float = 0.30
    optional_full_credit_count: int = 2


class KeywordHygieneConfig(BaseModel):
    no_content_score: float = 0.7
    duplicate_penalty_multiplier: float = 2.0
    suspicious_duplicate_threshold: float = 0.15


class ContentDensityConfig(BaseModel):
    no_bullets_score: float = 0.3
    min_ideal_words: int = 8
    max_ideal_words: int = 30
    min_words_per_page: int = 80
    sparse_content_score_cap: float = 0.5


#: Code-version identifier for the *algorithm* (dimension formulas). Bump
#: when formula shape changes, independent of ResumeQualityConfig.version
#: (which bumps for numeric-only retuning).
ALGORITHM_VERSION = "RESUME_QUALITY_V1"


class ResumeQualityConfig(BaseModel):
    version: str = "RESUME_QUALITY_CONFIG_V1"
    dimension_weights: QualityDimensionWeights = QualityDimensionWeights()
    parseability: ParseabilityConfig = ParseabilityConfig()
    structure: StructureConfig = StructureConfig()
    section_consistency: SectionConsistencyConfig = SectionConsistencyConfig()
    content_completeness: ContentCompletenessConfig = ContentCompletenessConfig()
    evidence_quality: EvidenceQualityConfig = EvidenceQualityConfig()
    date_consistency: DateConsistencyConfig = DateConsistencyConfig()
    contact_completeness: ContactCompletenessConfig = ContactCompletenessConfig()
    keyword_hygiene: KeywordHygieneConfig = KeywordHygieneConfig()
    content_density: ContentDensityConfig = ContentDensityConfig()


@lru_cache
def get_resume_quality_config() -> ResumeQualityConfig:
    """Single cached instance for now (config is code-defined), mirroring
    app.modules.scoring.config.get_scoring_config()'s pattern."""
    return ResumeQualityConfig()
