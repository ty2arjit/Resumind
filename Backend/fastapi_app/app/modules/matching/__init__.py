"""Hybrid Matching Engine (spec Phase 5).

Combines exact, canonical, keyword, TF-IDF, semantic, and context signals
into a preliminary match strength per requirement/evidence pair. This is
NOT the final ATS score — see app.modules.scoring for that (Phase 7).
"""

from app.modules.matching.evidence_index import build_evidence_index
from app.modules.matching.schemas import (
    EvidenceContext,
    ExperienceMatchSignals,
    HybridMatchResult,
    MatchableEvidence,
    MatchExplanation,
    MatchSignals,
    QualificationMatchSignals,
    ResponsibilityMatchSignals,
)
from app.modules.matching.service import MatchingService

__all__ = [
    "MatchingService",
    "build_evidence_index",
    "EvidenceContext",
    "MatchableEvidence",
    "MatchSignals",
    "MatchExplanation",
    "HybridMatchResult",
    "ResponsibilityMatchSignals",
    "ExperienceMatchSignals",
    "QualificationMatchSignals",
]
