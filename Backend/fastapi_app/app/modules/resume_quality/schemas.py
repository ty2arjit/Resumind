"""Resume Quality output schemas (spec Phase 8 §24, §28-30)."""

import enum

from pydantic import BaseModel


class QualityDimension(str, enum.Enum):
    PARSEABILITY = "PARSEABILITY"
    STRUCTURE = "STRUCTURE"
    CONTENT_COMPLETENESS = "CONTENT_COMPLETENESS"
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"
    DATE_CONSISTENCY = "DATE_CONSISTENCY"
    CONTACT_COMPLETENESS = "CONTACT_COMPLETENESS"
    KEYWORD_HYGIENE = "KEYWORD_HYGIENE"
    SECTION_CONSISTENCY = "SECTION_CONSISTENCY"
    CONTENT_DENSITY = "CONTENT_DENSITY"


class FindingSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FindingType(str, enum.Enum):
    PARSING_WARNING = "PARSING_WARNING"
    CONTENT_SIGNAL = "CONTENT_SIGNAL"
    STRUCTURE_SIGNAL = "STRUCTURE_SIGNAL"
    DUPLICATE_CONTENT = "DUPLICATE_CONTENT"
    DATE_SIGNAL = "DATE_SIGNAL"
    CONTACT_SIGNAL = "CONTACT_SIGNAL"


class QualityFinding(BaseModel):
    type: FindingType
    severity: FindingSeverity
    message_key: str
    dimension: QualityDimension


class QualityDimensionScores(BaseModel):
    """Each dimension is a 0.0-1.0 raw score (spec §24); the final 0-100
    ResumeQuality is a weighted aggregate of these, computed separately."""

    parseability: float
    structure: float
    content_completeness: float
    evidence_quality: float
    date_consistency: float
    contact_completeness: float
    keyword_hygiene: float
    section_consistency: float
    content_density: float


class ResumeQualityResult(BaseModel):
    resume_quality: int
    dimension_scores: QualityDimensionScores
    findings: list[QualityFinding]
    resume_quality_algorithm_version: str
    resume_quality_config_version: str
