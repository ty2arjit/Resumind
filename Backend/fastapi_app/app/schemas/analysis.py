import uuid
from datetime import datetime

from app.models.enums import AnalysisMode, AnalysisStatus, ImportanceLevel, MatchStrength, RequirementType
from app.schemas.common import ORMModel


class EvidenceRead(ORMModel):
    id: uuid.UUID
    text: str
    section: str | None
    technologies: list | None
    metrics: list | None
    relevance_score: float | None


class RequirementRead(ORMModel):
    id: uuid.UUID
    text: str
    type: RequirementType
    canonical_entity: str | None
    importance: ImportanceLevel
    critical: bool
    weight: float


class RequirementMatchRead(ORMModel):
    id: uuid.UUID
    requirement: RequirementRead
    match_strength: MatchStrength
    score: float | None
    evidence: list[EvidenceRead] = []


class RecommendationRead(ORMModel):
    id: uuid.UUID
    text: str
    category: str | None
    priority: int | None


class ScoreBreakdownRead(ORMModel):
    category: str
    score: float
    weight: float


class AnalysisRead(ORMModel):
    """Mirrors the conceptual Analysis Response shape in spec §49."""

    id: uuid.UUID
    mode: AnalysisMode
    status: AnalysisStatus
    algorithm_version: str | None

    ats_alignment_score: float | None
    resume_quality_score: float | None
    target_fit_score: float | None

    score_breakdowns: list[ScoreBreakdownRead] = []
    requirement_matches: list[RequirementMatchRead] = []
    recommendations: list[RecommendationRead] = []

    created_at: datetime
    completed_at: datetime | None


class AnalysisCreateRequest(ORMModel):
    """Mirrors spec §48's conceptual analysis request."""

    resume_version_id: uuid.UUID
    job_description_id: uuid.UUID | None = None
    target_profile_id: uuid.UUID | None = None
