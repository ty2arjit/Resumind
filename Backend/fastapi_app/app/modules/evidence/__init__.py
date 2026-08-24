"""Evidence Retrieval & Evidence Intelligence Engine (spec Phase 6).

Answers "what evidence in the resume supports this requirement?" — NOT
the final ATS score (Phase 7). Built entirely on top of Phase 5's
MatchingService; owns selecting, ranking, deduplicating, and aggregating
evidence, not matching itself.
"""

from app.modules.evidence.index import build_evidence_pool
from app.modules.evidence.schemas import (
    EvidenceItem,
    EvidenceQualitySignals,
    EvidenceSourceType,
    EvidenceStrength,
    ExperienceEvidence,
    QualificationEvidence,
    RankedEvidence,
    RequirementEvidenceResult,
)
from app.modules.evidence.service import EvidenceService

__all__ = [
    "EvidenceService",
    "build_evidence_pool",
    "EvidenceItem",
    "EvidenceSourceType",
    "EvidenceStrength",
    "EvidenceQualitySignals",
    "RankedEvidence",
    "ExperienceEvidence",
    "QualificationEvidence",
    "RequirementEvidenceResult",
]
