"""Recommendation generation (spec §12-18). Every recommendation is
derived from a detected Gap or resume-quality QualityFinding — never
invented, never claiming the candidate has a skill they haven't
demonstrated (spec §13 no-fabrication rule)."""

from app.modules.analysis.config import AnalysisConfig
from app.modules.analysis.schemas import AnalysisSource, Gap, GapType, Priority, Recommendation, RecommendationType
from app.modules.analysis.templates import render_message

_GAP_TYPE_TO_RECOMMENDATION_TYPE = {
    GapType.MISSING_REQUIREMENT: RecommendationType.ADDRESS_MISSING_REQUIREMENT,
    GapType.PARTIAL_REQUIREMENT: RecommendationType.ADD_EVIDENCE,
    GapType.WEAK_EVIDENCE: RecommendationType.STRENGTHEN_EVIDENCE,
    GapType.EXPERIENCE_GAP: RecommendationType.CLARIFY_EXPERIENCE,
    GapType.QUALIFICATION_GAP: RecommendationType.CLARIFY_QUALIFICATION,
    GapType.DOMAIN_GAP: RecommendationType.IMPROVE_DOMAIN_EVIDENCE,
}

_QUALITY_MESSAGE_KEY_TO_RECOMMENDATION_TYPE = {
    "PARSING_WARNING": RecommendationType.IMPROVE_PARSING,
    "REDUCE_KEYWORD_REPETITION": RecommendationType.REDUCE_KEYWORD_REPETITION,
    "ADD_METRIC_WHERE_ACCURATE": RecommendationType.ADD_METRIC_WHERE_ACCURATE,
    "CLARIFY_DATES": RecommendationType.IMPROVE_RESUME_STRUCTURE,
    "IMPROVE_CONTACT_INFO": RecommendationType.IMPROVE_RESUME_STRUCTURE,
    "IMPROVE_STRUCTURE": RecommendationType.IMPROVE_RESUME_STRUCTURE,
}


def generate_recommendations_from_gaps(gaps: list[Gap]) -> list[Recommendation]:
    recommendations = []
    for gap in gaps:
        if gap.type == GapType.RESUME_QUALITY_GAP:
            recommendation_type = _QUALITY_MESSAGE_KEY_TO_RECOMMENDATION_TYPE.get(
                gap.message_key, RecommendationType.IMPROVE_RESUME_STRUCTURE
            )
            message = render_message(gap.message_key, finding_key=gap.text)
        else:
            recommendation_type = _GAP_TYPE_TO_RECOMMENDATION_TYPE.get(gap.type, RecommendationType.ADD_EVIDENCE)
            message = render_message(gap.message_key, text=gap.text)

        recommendations.append(
            Recommendation(
                type=recommendation_type,
                priority=gap.priority,
                requirement_id=gap.requirement_id,
                message_key=gap.message_key,
                message=message,
                reason_code=gap.type.value,
                source=gap.source,
            )
        )
    return recommendations


def prioritize_recommendations(recommendations: list[Recommendation], config: AnalysisConfig) -> list[Recommendation]:
    priority_rank = {Priority.CRITICAL: 3, Priority.HIGH: 2, Priority.MEDIUM: 1, Priority.LOW: 0}
    source_rank = {AnalysisSource.JD: 2, AnalysisSource.TARGET_PROFILE: 1, AnalysisSource.RESUME_QUALITY: 0}

    ranked = sorted(
        recommendations,
        key=lambda r: (priority_rank.get(r.priority, 0), source_rank.get(r.source, 0), r.requirement_id or r.message_key),
        reverse=True,
    )
    return ranked[: config.limits.top_n_recommendations]
