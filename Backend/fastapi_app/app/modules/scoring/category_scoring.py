"""Category-level aggregation and duplicate suppression (spec §13-15, §19)."""

from app.modules.job.schemas import Requirement
from app.modules.scoring.config import get_scoring_config
from app.modules.scoring.schemas import CategoryScoreResult, RequirementScoreResult, ScoringCategory


def mark_duplicates(requirements: list[Requirement], scores: list[RequirementScoreResult]) -> None:
    """spec §19 — duplicate JD requirements must not inflate or deflate
    the score. Reuses Phase 3's own duplicate detection (no second dedup
    system); the first requirement in each duplicate group is kept as
    the representative, others are excluded from category aggregation
    but stay visible in the full requirements list for transparency.
    Mutates `scores` in place (sets duplicate_of).

    find_duplicate_groups is imported lazily: app.modules.job.requirements
    imports app.modules.scoring.config (for centralized weights), and
    since importing any submodule of a package first runs that package's
    __init__ (which eagerly exposes ScoringService, pulling this module
    in), a top-level import here would be circular.
    """
    from app.modules.job.requirements import find_duplicate_groups

    duplicate_groups = find_duplicate_groups(requirements)
    score_by_id = {s.requirement_id: s for s in scores}

    for group in duplicate_groups:
        representative_id = group[0].id
        for requirement in group[1:]:
            score = score_by_id.get(requirement.id)
            if score is not None:
                score.duplicate_of = representative_id


def score_categories(requirement_scores: list[RequirementScoreResult]) -> dict[ScoringCategory, CategoryScoreResult]:
    weights_config = get_scoring_config().category_weights
    by_category: dict[ScoringCategory, list[RequirementScoreResult]] = {}

    for result in requirement_scores:
        if result.duplicate_of is not None:
            continue
        by_category.setdefault(result.category, []).append(result)

    category_results: dict[ScoringCategory, CategoryScoreResult] = {}
    for category, results in by_category.items():
        total_weight = sum(r.weight for r in results)
        category_score = sum(r.score * r.weight for r in results) / total_weight if total_weight > 0 else 0.0
        configured_weight = getattr(weights_config, category.value.lower())

        category_results[category] = CategoryScoreResult(
            category=category,
            score=round(category_score, 6),
            configured_weight=configured_weight,
            normalized_weight=0.0,  # filled in by ats_engine once the active set is known
            requirement_count=len(results),
        )

    return category_results
