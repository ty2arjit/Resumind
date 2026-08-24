"""Analysis Engine output schemas (spec Phase 10 §3, §22)."""

import enum
import uuid

from pydantic import BaseModel, Field

from app.models.enums import AnalysisMode, AnalysisStatus
from app.modules.scoring.schemas import RequirementScoreResult


class Priority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class StrengthType(str, enum.Enum):
    STRONG_REQUIREMENT = "STRONG_REQUIREMENT"
    STRONG_CATEGORY_COVERAGE = "STRONG_CATEGORY_COVERAGE"
    STRONG_POSITION_FIT = "STRONG_POSITION_FIT"
    STRONG_DOMAIN_FIT = "STRONG_DOMAIN_FIT"
    HIGH_QUALITY_DIMENSION = "HIGH_QUALITY_DIMENSION"


class GapType(str, enum.Enum):
    MISSING_REQUIREMENT = "MISSING_REQUIREMENT"
    PARTIAL_REQUIREMENT = "PARTIAL_REQUIREMENT"
    WEAK_EVIDENCE = "WEAK_EVIDENCE"
    EXPERIENCE_GAP = "EXPERIENCE_GAP"
    QUALIFICATION_GAP = "QUALIFICATION_GAP"
    DOMAIN_GAP = "DOMAIN_GAP"
    RESUME_QUALITY_GAP = "RESUME_QUALITY_GAP"


class RecommendationType(str, enum.Enum):
    ADD_EVIDENCE = "ADD_EVIDENCE"
    STRENGTHEN_EVIDENCE = "STRENGTHEN_EVIDENCE"
    CLARIFY_EXPERIENCE = "CLARIFY_EXPERIENCE"
    ADDRESS_MISSING_REQUIREMENT = "ADDRESS_MISSING_REQUIREMENT"
    IMPROVE_RESUME_STRUCTURE = "IMPROVE_RESUME_STRUCTURE"
    IMPROVE_PARSING = "IMPROVE_PARSING"
    REDUCE_KEYWORD_REPETITION = "REDUCE_KEYWORD_REPETITION"
    ADD_METRIC_WHERE_ACCURATE = "ADD_METRIC_WHERE_ACCURATE"
    CLARIFY_QUALIFICATION = "CLARIFY_QUALIFICATION"
    IMPROVE_DOMAIN_EVIDENCE = "IMPROVE_DOMAIN_EVIDENCE"


class AnalysisSource(str, enum.Enum):
    """spec §21 — combined mode must keep JD-sourced and Target-Profile
    -sourced findings distinguishable; JD is always authoritative."""

    JD = "JD"
    TARGET_PROFILE = "TARGET_PROFILE"
    RESUME_QUALITY = "RESUME_QUALITY"


class Strength(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: StrengthType
    requirement_id: str | None = None
    text: str
    category: str | None = None
    status: str | None = None
    priority: Priority
    source: AnalysisSource = AnalysisSource.JD


class GapDetail(BaseModel):
    what_is_satisfied: str | None = None
    what_is_missing: str | None = None


class Gap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: GapType
    priority: Priority
    requirement_id: str | None = None
    text: str
    category: str | None = None
    status: str
    message_key: str
    details: GapDetail = GapDetail()
    source: AnalysisSource = AnalysisSource.JD


class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: RecommendationType
    priority: Priority
    requirement_id: str | None = None
    message_key: str
    message: str
    reason_code: str
    source: AnalysisSource = AnalysisSource.JD


class AnalysisContext(BaseModel):
    mode: AnalysisMode
    resume_version_id: str | None = None
    job_description_id: str | None = None
    target_profile_position: str | None = None
    target_profile_domain: str | None = None


class AnalysisScores(BaseModel):
    ats_alignment: int | None = None
    resume_quality: int | None = None
    target_fit: int | None = None
    position_fit: int | None = None
    domain_fit: int | None = None


class AlgorithmVersions(BaseModel):
    analysis: str
    ats: str | None = None
    resume_quality: str | None = None
    target_fit: str | None = None
    matching: str | None = None
    knowledge: str | None = None


class AnalysisSummary(BaseModel):
    primary_score: int
    score_type: str
    strongest_area: str | None = None
    weakest_area: str | None = None
    critical_gap_count: int
    high_priority_gap_count: int


class Analysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: AnalysisStatus = AnalysisStatus.COMPLETED
    context: AnalysisContext
    scores: AnalysisScores

    strengths: list[Strength] = []
    gaps: list[Gap] = []
    missing_requirements: list[str] = []
    partial_requirements: list[str] = []
    weak_evidence: list[str] = []
    recommendations: list[Recommendation] = []

    # Pass-through of Phase 7's own category breakdown and per-requirement
    # scores (already computed by ScoringService/TargetProfileService) —
    # exposed here so the frontend can render score-breakdown and
    # "how was this calculated" transparency views (spec Phase 12 §22-23)
    # without the Analysis Engine recalculating anything itself.
    categories: dict[str, dict] | None = None
    requirements: list[RequirementScoreResult] = []

    summary: AnalysisSummary
    algorithm_versions: AlgorithmVersions


class ResumeComparisonResult(BaseModel):
    """spec §24 — architecture only; no comparison UI in this phase."""

    score_delta: int
    new_strengths: list[str]
    resolved_gaps: list[str]
    new_gaps: list[str]
