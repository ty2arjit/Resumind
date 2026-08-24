"""Final ATS Alignment score (spec §15-17, §24).

Active-category weight normalization (spec §15): a JD without a
Qualifications section must not silently score that category as 0 —
instead the *active* categories' configured weights are renormalized to
sum to 1.0, and only those contribute to the final score.
"""

from app.modules.scoring.schemas import CategoryScoreResult, RequirementScoreResult, ScoringCategory


def normalize_active_category_weights(
    category_results: dict[ScoringCategory, CategoryScoreResult],
) -> dict[ScoringCategory, CategoryScoreResult]:
    active_weight_total = sum(r.configured_weight for r in category_results.values())
    if active_weight_total == 0:
        return category_results

    return {
        category: result.model_copy(update={"normalized_weight": result.configured_weight / active_weight_total})
        for category, result in category_results.items()
    }


def calculate_ats_score(category_results: dict[ScoringCategory, CategoryScoreResult]) -> int:
    """spec §16-17 — ATS Score = sum(active_category_score * normalized_weight),
    display_score = round(score * 100), always bounded to [0, 100]."""
    if not category_results:
        return 0

    weighted_sum = sum(result.score * result.normalized_weight for result in category_results.values())
    ats_score = max(0.0, min(1.0, weighted_sum))
    return max(0, min(100, round(ats_score * 100)))


def calculate_contributions(
    requirement_scores: list[RequirementScoreResult], category_results: dict[ScoringCategory, CategoryScoreResult]
) -> None:
    """spec §24 — how much each requirement contributed to the final 0-100
    score, e.g. "your missing Kubernetes requirement reduced your score
    by 6.8 points." Mutates `requirement_scores` in place.
    """
    category_weight_totals: dict[ScoringCategory, float] = {}
    for result in requirement_scores:
        if result.duplicate_of is not None:
            continue
        category_weight_totals[result.category] = category_weight_totals.get(result.category, 0.0) + result.weight

    for result in requirement_scores:
        if result.duplicate_of is not None:
            result.contribution = 0.0
            continue
        category = category_results.get(result.category)
        total_weight = category_weight_totals.get(result.category, 0.0)
        if category is None or total_weight == 0:
            result.contribution = 0.0
            continue
        share_of_category = result.weight / total_weight
        result.contribution = round(result.score * share_of_category * category.normalized_weight * 100, 4)
