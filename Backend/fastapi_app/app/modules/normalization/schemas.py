"""Normalization output schemas (spec §5, §7, §8, §16)."""

import enum

from pydantic import BaseModel, Field


class EntityType(str, enum.Enum):
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    LIBRARY = "LIBRARY"
    DATABASE = "DATABASE"
    CLOUD = "CLOUD"
    DEVOPS = "DEVOPS"
    TOOL = "TOOL"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    SOFTWARE = "SOFTWARE"
    ROLE = "ROLE"
    DOMAIN = "DOMAIN"
    OTHER = "OTHER"


class NormalizationMethod(str, enum.Enum):
    EXACT = "EXACT"
    CASE_NORMALIZATION = "CASE_NORMALIZATION"
    FORMATTING_NORMALIZATION = "FORMATTING_NORMALIZATION"
    ALIAS = "ALIAS"
    MANUAL_MAPPING = "MANUAL_MAPPING"
    UNKNOWN = "UNKNOWN"


class NormalizationStatus(str, enum.Enum):
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"


class NormalizedEntity(BaseModel):
    raw_value: str
    normalized_text: str
    canonical_value: str | None = None
    entity_type: EntityType | None = None
    normalization_method: NormalizationMethod
    normalization_status: NormalizationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    knowledge_version: str


class NormalizedRole(BaseModel):
    raw_role: str
    normalized_text: str
    canonical_role: str | None = None
    parent_role: str | None = None
    normalization_method: NormalizationMethod
    normalization_status: NormalizationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    knowledge_version: str


class NormalizedDomain(BaseModel):
    raw_domain: str
    normalized_text: str
    canonical_domain: str | None = None
    parent_domain: str | None = None
    normalization_method: NormalizationMethod
    normalization_status: NormalizationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    knowledge_version: str


class NormalizedAction(BaseModel):
    raw_action: str
    normalized_text: str
    canonical_action: str | None = None
    normalization_method: NormalizationMethod
    normalization_status: NormalizationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    knowledge_version: str


class NormalizedSkillSet(BaseModel):
    """Output of batch-normalizing every raw skill/technology mention
    found across a structured resume or JD (spec §17). One entry per
    unique raw mention — grouping by canonical_value (spec §9) is a
    trivial reduction over this list, left to the caller rather than
    baked in here.
    """

    skills: list[NormalizedEntity] = []
    knowledge_version: str
