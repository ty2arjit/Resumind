"""Evaluation metrics (spec Phase 13 §27-28). Pure functions over
already-computed CaseResult data — never recomputes matching/scoring."""

import statistics

from app.modules.evaluation.schemas import (
    CaseResult,
    ConfusionCounts,
    MatchingMetrics,
    RequirementCaseResult,
    ScoreStatistics,
)

_STRONG_BUCKETS = {"matches", "STRONG", "VERY_STRONG"}


def _is_positive_bucket(bucket_or_status: str) -> bool:
    return bucket_or_status in ("matches", "STRONG", "VERY_STRONG")


def compute_matching_metrics(all_requirement_results: list[RequirementCaseResult]) -> MatchingMetrics:
    """Binary precision/recall/F1 over "is this requirement satisfied"
    (positive = STRONG/VERY_STRONG bucket), plus exact 4-way bucket
    accuracy (matches/partial/missing/unknown)."""
    counts = ConfusionCounts()
    exact_correct = 0

    for result in all_requirement_results:
        expected_positive = _is_positive_bucket(result.expected_bucket)
        actual_positive = result.actual_status in ("STRONG", "VERY_STRONG")

        if expected_positive and actual_positive:
            counts.true_positive += 1
        elif not expected_positive and actual_positive:
            counts.false_positive += 1
        elif not expected_positive and not actual_positive:
            counts.true_negative += 1
        else:
            counts.false_negative += 1

        if result.correct:
            exact_correct += 1

    precision = counts.true_positive / (counts.true_positive + counts.false_positive) if (counts.true_positive + counts.false_positive) else None
    recall = counts.true_positive / (counts.true_positive + counts.false_negative) if (counts.true_positive + counts.false_negative) else None
    f1 = (2 * precision * recall / (precision + recall)) if precision and recall and (precision + recall) else None
    bucket_accuracy = exact_correct / len(all_requirement_results) if all_requirement_results else None

    return MatchingMetrics(precision=precision, recall=recall, f1=f1, counts=counts, bucket_accuracy=bucket_accuracy)


def compute_score_statistics(scores: list[float]) -> ScoreStatistics:
    if not scores:
        return ScoreStatistics(count=0, minimum=0, maximum=0, mean=0, near_zero_count=0, near_hundred_count=0)
    return ScoreStatistics(
        count=len(scores),
        minimum=min(scores),
        maximum=max(scores),
        mean=statistics.mean(scores),
        near_zero_count=sum(1 for s in scores if s <= 10),
        near_hundred_count=sum(1 for s in scores if s >= 90),
    )
