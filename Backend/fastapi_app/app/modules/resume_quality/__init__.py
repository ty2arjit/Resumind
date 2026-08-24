"""Resume Quality & ATS-Friendliness Engine (spec Phase 8).

Answers "how technically sound, parseable, structured and evidence-rich
is this resume?" — deliberately independent of any Job Description and
of the ATS Alignment engine (Phase 7). No LLM is used anywhere in this
module; every score/finding comes from deterministic application logic.
"""

from app.modules.resume_quality.config import ALGORITHM_VERSION, ResumeQualityConfig, get_resume_quality_config
from app.modules.resume_quality.schemas import (
    FindingSeverity,
    FindingType,
    QualityDimension,
    QualityDimensionScores,
    QualityFinding,
    ResumeQualityResult,
)
from app.modules.resume_quality.service import ResumeQualityService

__all__ = [
    "ALGORITHM_VERSION",
    "ResumeQualityConfig",
    "get_resume_quality_config",
    "ResumeQualityService",
    "ResumeQualityResult",
    "QualityDimensionScores",
    "QualityFinding",
    "QualityDimension",
    "FindingSeverity",
    "FindingType",
]
