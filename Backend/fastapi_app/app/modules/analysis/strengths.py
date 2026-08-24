"""Strength detection (spec §4-5). Derived only from actual structured
requirement scores — never invented from generic resume content."""

from app.modules.analysis.config import AnalysisConfig
from app.modules.analysis.schemas import AnalysisSource, Priority, Strength, StrengthType
from app.modules.resume_quality.schemas import QualityDimensionScores
from app.modules.scoring.schemas import RequirementScoreResult

_STATUS_RANK = {"MISSING": 0, "UNKNOWN": 0, "WEAK": 1, "PARTIAL": 2, "STRONG": 3, "VERY_STRONG": 4}


def _requirement_priority(requirement: RequirementScoreResult) -> Priority:
    if requirement.status == "VERY_STRONG" and requirement.importance == "REQUIRED":
        return Priority.HIGH
    if requirement.status == "VERY_STRONG":
        return Priority.MEDIUM
    return Priority.LOW


def detect_requirement_strengths(
    requirement_scores: list[RequirementScoreResult], config: AnalysisConfig, source: AnalysisSource = AnalysisSource.JD
) -> list[Strength]:
    strengths = []
    for requirement in requirement_scores:
        if requirement.duplicate_of is not None:
            continue
        if _STATUS_RANK.get(requirement.status, 0) < config.strength_thresholds.minimum_status_rank:
            continue
        strengths.append(
            Strength(
                type=StrengthType.STRONG_REQUIREMENT,
                requirement_id=requirement.requirement_id,
                text=requirement.text,
                category=requirement.category.value,
                status=requirement.status,
                priority=_requirement_priority(requirement),
                source=source,
            )
        )
    return strengths


def detect_fit_strengths(position_fit: int | None, domain_fit: int | None, config: AnalysisConfig) -> list[Strength]:
    strengths = []
    threshold = config.strength_thresholds.strong_fit_threshold
    if position_fit is not None and position_fit >= threshold:
        strengths.append(
            Strength(
                type=StrengthType.STRONG_POSITION_FIT,
                text=f"Strong alignment with the target position ({position_fit}/100).",
                priority=Priority.MEDIUM,
                source=AnalysisSource.TARGET_PROFILE,
            )
        )
    if domain_fit is not None and domain_fit >= threshold:
        strengths.append(
            Strength(
                type=StrengthType.STRONG_DOMAIN_FIT,
                text=f"Strong demonstrated domain evidence ({domain_fit}/100).",
                priority=Priority.MEDIUM,
                source=AnalysisSource.TARGET_PROFILE,
            )
        )
    return strengths


def detect_quality_strengths(dimension_scores: QualityDimensionScores, config: AnalysisConfig) -> list[Strength]:
    threshold = config.strength_thresholds.high_quality_dimension_threshold
    strengths = []
    for dimension, score in dimension_scores.model_dump().items():
        if score >= threshold:
            strengths.append(
                Strength(
                    type=StrengthType.HIGH_QUALITY_DIMENSION,
                    text=f"{dimension.replace('_', ' ').title()} is strong.",
                    category=dimension.upper(),
                    priority=Priority.LOW,
                    source=AnalysisSource.RESUME_QUALITY,
                )
            )
    return strengths


def prioritize_strengths(strengths: list[Strength], config: AnalysisConfig) -> list[Strength]:
    """spec §5 — requirement importance first, then status strength, then
    a stable requirement_id tiebreaker for determinism."""
    priority_rank = {Priority.CRITICAL: 3, Priority.HIGH: 2, Priority.MEDIUM: 1, Priority.LOW: 0}
    status_rank = {"VERY_STRONG": 1, "STRONG": 0}

    ranked = sorted(
        strengths,
        key=lambda s: (
            priority_rank.get(s.priority, 0),
            status_rank.get(s.status or "", -1),
            s.requirement_id or s.text,
        ),
        reverse=True,
    )
    return ranked[: config.limits.top_n_strengths]
