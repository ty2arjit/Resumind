"""Analysis & Recommendation Engine (spec Phase 10).

A pure interpretation layer over Phases 2-9: it detects strengths/gaps
from their already-computed structured outputs and generates
deterministic, traceable, template-based recommendations. No LLM, no
re-implementation of parsing/normalization/matching/evidence/scoring.
"""

from app.modules.analysis.config import ALGORITHM_VERSION, AnalysisConfig, get_analysis_config
from app.modules.analysis.schemas import (
    AlgorithmVersions,
    Analysis,
    AnalysisContext,
    AnalysisScores,
    AnalysisSource,
    AnalysisSummary,
    Gap,
    GapType,
    Priority,
    Recommendation,
    RecommendationType,
    ResumeComparisonResult,
    Strength,
    StrengthType,
)
from app.modules.analysis.service import AnalysisService

__all__ = [
    "ALGORITHM_VERSION",
    "AnalysisConfig",
    "get_analysis_config",
    "AnalysisService",
    "Analysis",
    "AnalysisContext",
    "AnalysisScores",
    "AnalysisSummary",
    "AlgorithmVersions",
    "AnalysisSource",
    "Strength",
    "StrengthType",
    "Gap",
    "GapType",
    "Priority",
    "Recommendation",
    "RecommendationType",
    "ResumeComparisonResult",
]
