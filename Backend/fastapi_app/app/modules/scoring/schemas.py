"""Deterministic ATS Scoring schemas (spec Phase 7 §4, §24-25, §49)."""

import enum

from pydantic import BaseModel, Field


class ScoringCategory(str, enum.Enum):
    REQUIRED_SKILLS = "REQUIRED_SKILLS"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    EXPERIENCE = "EXPERIENCE"
    QUALIFICATIONS = "QUALIFICATIONS"
    PREFERRED_SKILLS = "PREFERRED_SKILLS"
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"
    OTHER = "OTHER"


class RequirementScoreResult(BaseModel):
    """spec §4, §24 — one requirement's score, status, and its
    contribution to the final ATS score. NOT itself the final score."""

    requirement_id: str
    text: str
    category: ScoringCategory
    status: str  # MatchStrength value, or "UNKNOWN"
    score: float = Field(ge=0.0, le=1.0)
    importance: str
    weight: float
    critical: bool = False
    contribution: float = 0.0
    duplicate_of: str | None = None  # set when this requirement was suppressed as a duplicate (spec §19)

    # Display-only pass-through of the top-ranked evidence Phase 6 already
    # retrieved (RequirementEvidenceResult.evidence[0]) — added for the
    # frontend Evidence Explorer (frontendReadme.md §21). Never used in
    # any score/weight/threshold computation.
    evidence_text: str | None = None
    evidence_source: str | None = None


class CategoryScoreResult(BaseModel):
    """spec §14, §25."""

    category: ScoringCategory
    score: float = Field(ge=0.0, le=1.0)
    configured_weight: float
    normalized_weight: float
    requirement_count: int


class ScoreBreakdown(BaseModel):
    """spec §25, §49 — the complete, explainable result. Every number
    here must be reconstructable from Requirement -> Matching signals ->
    Evidence -> Requirement score -> Category score -> Final score."""

    ats_alignment: int = Field(ge=0, le=100)
    categories: dict[str, CategoryScoreResult]
    requirements: list[RequirementScoreResult]

    algorithm_version: str
    scoring_config_version: str
    knowledge_version: str | None = None
    embedding_model_version: str | None = None
