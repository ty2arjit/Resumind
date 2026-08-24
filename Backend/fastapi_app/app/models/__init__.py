"""Importing this module registers every table on Base.metadata.

Import order matters for forward-referenced relationship() strings: all
models must be imported at least once before any relationship is resolved
(e.g. in tests that call `Base.metadata.create_all`).
"""

from app.db.base import Base
from app.models.analysis import Analysis
from app.models.evaluation import EvaluationCase, EvaluationResult
from app.models.evidence import Evidence
from app.models.job_description import JobDescription
from app.models.recommendation import Recommendation
from app.models.requirement import Requirement
from app.models.requirement_match import RequirementMatch
from app.models.resume import Resume, ResumeVersion
from app.models.score_breakdown import ScoreBreakdown
from app.models.target_profile import TargetProfile
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Resume",
    "ResumeVersion",
    "JobDescription",
    "TargetProfile",
    "Analysis",
    "Requirement",
    "RequirementMatch",
    "Evidence",
    "Recommendation",
    "ScoreBreakdown",
    "EvaluationCase",
    "EvaluationResult",
]
