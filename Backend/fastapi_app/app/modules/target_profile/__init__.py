"""Target Profile Intelligence Engine (spec Phase 9).

Supports Mode B analysis — Resume + Position + Domain -> Target Fit —
as a curated, deterministic, versioned alternative to Mode A's
JD-based ATS Alignment (Phase 7). Reuses Phase 4 normalization, Phase 5
matching, and Phase 6 evidence retrieval verbatim; no second matching
system and no LLM anywhere in this module.
"""

from app.modules.target_profile.config import ALGORITHM_VERSION, TargetProfileConfig, get_target_profile_config
from app.modules.target_profile.errors import DomainNotSupportedError, PositionNotSupportedError
from app.modules.target_profile.registry import TargetProfileRegistry
from app.modules.target_profile.schemas import (
    CustomRequirements,
    EffectiveTargetProfile,
    TargetAnalysisResult,
    TargetFitScores,
    TargetProfile,
)
from app.modules.target_profile.service import TargetProfileService

__all__ = [
    "ALGORITHM_VERSION",
    "TargetProfileConfig",
    "get_target_profile_config",
    "TargetProfileRegistry",
    "TargetProfileService",
    "TargetProfile",
    "EffectiveTargetProfile",
    "CustomRequirements",
    "TargetAnalysisResult",
    "TargetFitScores",
    "PositionNotSupportedError",
    "DomainNotSupportedError",
]
