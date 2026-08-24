"""Target Profile schemas (spec Phase 9 §8, §28)."""

import enum
import uuid

from pydantic import BaseModel, Field

from app.modules.scoring.schemas import RequirementScoreResult


class PositionRef(BaseModel):
    raw: str
    canonical: str | None = None


class DomainRef(BaseModel):
    raw: str | None = None
    canonical: str | None = None


class CustomRequirements(BaseModel):
    """User-supplied additions to a base profile (spec §10-11). Stored
    separately from the base profile — never mutates it."""

    core_skills: list[str] = []
    technologies: list[str] = []
    responsibilities: list[str] = []
    domain_knowledge: list[str] = []
    experience_expectations: list[str] = []
    preferred_skills: list[str] = []


class TargetProfileCategories(BaseModel):
    core_skills: list[str] = []
    technologies: list[str] = []
    responsibilities: list[str] = []
    domain_knowledge: list[str] = []
    experience_expectations: list[str] = []
    preferred_skills: list[str] = []


class TargetProfile(BaseModel):
    """The base (curated) profile for a Position + Domain combination —
    before any user customization is applied (spec §8)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: PositionRef
    domain: DomainRef
    core_skills: list[str] = []
    technologies: list[str] = []
    responsibilities: list[str] = []
    domain_knowledge: list[str] = []
    experience_expectations: list[str] = []
    preferred_skills: list[str] = []
    knowledge_version: str
    profile_version: str


class EffectiveTargetProfile(BaseModel):
    """Base Profile + User Custom Requirements (spec §10), with custom
    requirements taking priority (spec §11) but both preserved separately
    so the UI can distinguish "expected for this role" from "your custom
    requirement"."""

    base_profile: TargetProfile
    custom_requirements: CustomRequirements
    effective: TargetProfileCategories


class TargetRequirementCategory(str, enum.Enum):
    CORE_SKILLS = "CORE_SKILLS"
    TECHNOLOGIES = "TECHNOLOGIES"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    EXPERIENCE = "EXPERIENCE"
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"
    PREFERRED_SKILLS = "PREFERRED_SKILLS"
    OTHER = "OTHER"


class TargetFitScores(BaseModel):
    target_fit: int
    position_fit: int
    domain_fit: int


class TargetAnalysisResult(BaseModel):
    target_profile: TargetProfile
    scores: TargetFitScores
    requirements: list[RequirementScoreResult]
    matched_requirements: list[str]
    partial_requirements: list[str]
    missing_requirements: list[str]
    algorithm_version: str
    profile_config_version: str
    knowledge_version: str
