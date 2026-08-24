"""Evidence Engine schemas (spec Phase 6 §3, §10, §22)."""

import enum

from pydantic import BaseModel, Field

from app.models.enums import MatchStrength


class EvidenceSourceType(str, enum.Enum):
    EXPERIENCE_BULLET = "EXPERIENCE_BULLET"
    PROJECT_BULLET = "PROJECT_BULLET"
    SKILLS_SECTION = "SKILLS_SECTION"
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    SUMMARY = "SUMMARY"
    ACHIEVEMENT = "ACHIEVEMENT"
    LEADERSHIP = "LEADERSHIP"
    OTHER = "OTHER"


class EvidenceStrength(str, enum.Enum):
    MISSING = "MISSING"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class EvidenceItem(BaseModel):
    """spec §3 — a candidate piece of resume evidence, independent of any
    requirement. The `objects` field is intrinsic to the bullet itself
    (Phase 2's evidence extraction), unlike relevance/quality signals
    which only make sense relative to a specific requirement."""

    id: str
    resume_version_id: str | None = None
    text: str
    section: EvidenceSourceType
    source_type: str
    source_id: str | None = None
    position: str | None = None
    organization: str | None = None
    technologies: list[str] = []
    actions: list[str] = []
    metrics: list[str] = []
    objects: list[str] = []


class EvidenceQualitySignals(BaseModel):
    """spec §10 — per-requirement quality signals for one evidence item."""

    relevance: float = 0.0
    semantic_similarity: float | None = None
    lexical_relevance: float = 0.0
    canonical_entity_match: float = 0.0
    context_strength: float = 0.0
    action_match: float | None = None
    object_match: float | None = None
    technology_match: float | None = None
    metric_presence: float = 0.0


class RankedEvidence(BaseModel):
    evidence_id: str
    text: str
    section: EvidenceSourceType
    position: str | None = None
    strength: EvidenceStrength
    signals: EvidenceQualitySignals


class ExperienceEvidence(BaseModel):
    """spec §20."""

    required_years: float | None = None
    detected_relevant_years: float | None = None
    date_confidence: float = 0.0
    supporting_experience: list[str] = []


class QualificationEvidence(BaseModel):
    """spec §21."""

    degree: str | None = None
    field: str | None = None
    institution: str | None = None
    evidence_text: str | None = None
    matched: bool = False
    uncertain: bool = True


class RequirementEvidenceResult(BaseModel):
    """spec §22 — the top-level result for one requirement. Still NOT an
    ATS score (spec §23)."""

    requirement_id: str
    match_result: MatchStrength
    evidence: list[RankedEvidence] = []
    aggregated_evidence_strength: float = Field(ge=0.0, le=1.0, default=0.0)
    evidence_diversity: float = Field(ge=0.0, le=1.0, default=0.0)
    experience: ExperienceEvidence | None = None
    qualification: QualificationEvidence | None = None
    warnings: list[str] = []
