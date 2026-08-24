"""Normalization & Knowledge Engine (spec Phase 4).

Transforms raw resume/JD entities into canonical representations the
matching engine (Phase 5) can safely compare — controlled equivalence,
never embeddings-based fuzzy merging, and always deterministic.
"""

from app.modules.normalization.schemas import (
    EntityType,
    NormalizationMethod,
    NormalizationStatus,
    NormalizedAction,
    NormalizedDomain,
    NormalizedEntity,
    NormalizedRole,
    NormalizedSkillSet,
)
from app.modules.normalization.service import NormalizationService, group_by_canonical

__all__ = [
    "NormalizationService",
    "group_by_canonical",
    "EntityType",
    "NormalizationMethod",
    "NormalizationStatus",
    "NormalizedEntity",
    "NormalizedRole",
    "NormalizedDomain",
    "NormalizedAction",
    "NormalizedSkillSet",
]
