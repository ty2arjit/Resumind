"""Gap detection and prioritization (spec §6-11). MISSING vs UNKNOWN stays
distinct throughout — UNKNOWN never becomes a gap (spec §7)."""

from app.modules.analysis.config import AnalysisConfig
from app.modules.analysis.schemas import AnalysisSource, Gap, GapDetail, GapType, Priority
from app.modules.resume_quality.schemas import FindingSeverity, QualityFinding
from app.modules.scoring.schemas import RequirementScoreResult

_GAP_STATUSES = {"MISSING", "WEAK", "PARTIAL"}

_GAP_DETAILS = {
    "MISSING": GapDetail(what_is_satisfied=None, what_is_missing="No reliable evidence found for this requirement."),
    "WEAK": GapDetail(
        what_is_satisfied="The skill/requirement is mentioned in the resume.",
        what_is_missing="It is not demonstrated with project or experience evidence.",
    ),
    "PARTIAL": GapDetail(
        what_is_satisfied="Some relevant evidence was found.",
        what_is_missing="The evidence does not fully satisfy the requirement.",
    ),
}


def _gap_type(requirement: RequirementScoreResult) -> GapType:
    category = requirement.category.value
    if category == "DOMAIN_KNOWLEDGE":
        return GapType.DOMAIN_GAP
    if category == "EXPERIENCE":
        return GapType.EXPERIENCE_GAP
    if category == "QUALIFICATIONS":
        return GapType.QUALIFICATION_GAP
    if requirement.status == "WEAK":
        return GapType.WEAK_EVIDENCE
    if requirement.status == "MISSING":
        return GapType.MISSING_REQUIREMENT
    return GapType.PARTIAL_REQUIREMENT


def _message_key(requirement: RequirementScoreResult, gap_type: GapType) -> str:
    if gap_type == GapType.EXPERIENCE_GAP:
        return "EXPERIENCE_SHORTFALL" if requirement.status != "UNKNOWN" else "EXPERIENCE_UNKNOWN"
    if gap_type == GapType.QUALIFICATION_GAP:
        return "MISSING_QUALIFICATION"
    if gap_type == GapType.DOMAIN_GAP:
        return "MISSING_DOMAIN_KNOWLEDGE"
    if gap_type == GapType.WEAK_EVIDENCE:
        return "STRENGTHEN_SKILL_EVIDENCE"
    if requirement.status == "MISSING":
        return "MISSING_REQUIRED_SKILL" if requirement.importance == "REQUIRED" else "MISSING_PREFERRED_SKILL"
    return "PARTIAL_REQUIREMENT"


def impact_score(requirement: RequirementScoreResult, category_normalized_weight: float, config: AnalysisConfig) -> float:
    """spec §10-11 — a relative ranking signal built only from
    already-computed Phase 3/7 fields (importance, weight, category's
    normalized_weight); never a recalculation of the ATS score itself."""
    importance_weight = config.importance_weights.for_importance(requirement.importance)
    return importance_weight * category_normalized_weight * requirement.weight


def gap_priority(requirement: RequirementScoreResult, impact: float, config: AnalysisConfig) -> Priority:
    thresholds = config.gap_priority_thresholds
    if requirement.critical and requirement.status == "MISSING":
        return Priority.CRITICAL
    if requirement.status == "MISSING" and requirement.importance == "REQUIRED":
        return Priority.CRITICAL if impact >= thresholds.critical_impact else Priority.HIGH
    if requirement.status in ("MISSING", "WEAK"):
        return Priority.HIGH if impact >= thresholds.high_impact else Priority.MEDIUM
    return Priority.MEDIUM if impact >= thresholds.medium_impact else Priority.LOW


def detect_requirement_gaps(
    requirement_scores: list[RequirementScoreResult],
    category_normalized_weights: dict[str, float],
    config: AnalysisConfig,
    source: AnalysisSource = AnalysisSource.JD,
) -> list[Gap]:
    gaps = []
    for requirement in requirement_scores:
        if requirement.duplicate_of is not None:
            continue
        if requirement.status not in _GAP_STATUSES:
            continue  # UNKNOWN and strong matches are never gaps (spec §7)

        gap_type = _gap_type(requirement)
        category_weight = category_normalized_weights.get(requirement.category.value, 0.0)
        impact = impact_score(requirement, category_weight, config)

        gaps.append(
            Gap(
                type=gap_type,
                priority=gap_priority(requirement, impact, config),
                requirement_id=requirement.requirement_id,
                text=requirement.text,
                category=requirement.category.value,
                status=requirement.status,
                message_key=_message_key(requirement, gap_type),
                details=_GAP_DETAILS.get(requirement.status, GapDetail()),
                source=source,
            )
        )
    return gaps


_QUALITY_FINDING_TO_MESSAGE_KEY = {
    "PARSING_WARNING": "PARSING_WARNING",
    "DUPLICATE_CONTENT": "REDUCE_KEYWORD_REPETITION",
    "DATE_SIGNAL": "CLARIFY_DATES",
    "CONTACT_SIGNAL": "IMPROVE_CONTACT_INFO",
    "STRUCTURE_SIGNAL": "IMPROVE_STRUCTURE",
}

_SEVERITY_TO_PRIORITY = {
    FindingSeverity.HIGH: Priority.HIGH,
    FindingSeverity.MEDIUM: Priority.MEDIUM,
    FindingSeverity.LOW: Priority.LOW,
    FindingSeverity.INFO: Priority.LOW,
}


def detect_resume_quality_gaps(findings: list[QualityFinding], config: AnalysisConfig) -> list[Gap]:
    """spec §19 — consumes Phase 8 findings directly; never recomputes
    Resume Quality itself."""
    gaps = []
    for finding in findings:
        message_key = (
            "ADD_METRIC_WHERE_ACCURATE"
            if finding.message_key == "FEW_MEASURABLE_RESULTS"
            else _QUALITY_FINDING_TO_MESSAGE_KEY.get(finding.type.value, "IMPROVE_STRUCTURE")
        )
        gaps.append(
            Gap(
                type=GapType.RESUME_QUALITY_GAP,
                priority=_SEVERITY_TO_PRIORITY.get(finding.severity, Priority.LOW),
                text=finding.message_key,
                category=finding.dimension.value,
                status=finding.severity.value,
                message_key=message_key,
                source=AnalysisSource.RESUME_QUALITY,
            )
        )
    return gaps
