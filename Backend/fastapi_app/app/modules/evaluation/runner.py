"""Evaluation runner (spec Phase 13 §2). Runs the REAL Phase 2/3/7
pipeline (ResumeParser -> JD parser -> ScoringService) against each
dataset case and compares outputs to labeled expectations. Never
reimplements or bypasses production parsing/matching/scoring — this
module is read-only with respect to those pipelines.
"""

import time

from app.modules.evaluation.dataset import CASES, DATASET_VERSION
from app.modules.evaluation.metrics import compute_matching_metrics, compute_score_statistics
from app.modules.evaluation.schemas import (
    CaseResult,
    ErrorAnalysisEntry,
    EvaluationCase,
    EvaluationReport,
    PerformanceBenchmark,
    RequirementCaseResult,
)
from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.scoring import ScoringService
from app.modules.scoring.config import ALGORITHM_VERSION, get_scoring_config
from tests.fixtures.builders import build_pdf

_STATUS_TO_BUCKET = {
    "STRONG": "matches",
    "VERY_STRONG": "matches",
    "PARTIAL": "partial",
    "WEAK": "partial",
    "MISSING": "missing",
    "UNKNOWN": "unknown",
}


def _expected_bucket_for(case: EvaluationCase, requirement_text: str) -> str | None:
    if requirement_text in case.expected.matches:
        return "matches"
    if requirement_text in case.expected.partial:
        return "partial"
    if requirement_text in case.expected.missing:
        return "missing"
    if requirement_text in case.expected.unknown:
        return "unknown"
    return None


def run_case(case: EvaluationCase, service: ScoringService, timings: dict[str, list[float]]) -> CaseResult:
    t0 = time.perf_counter()
    resume = parse_pdf_bytes(build_pdf([case.resume_text]))
    timings.setdefault("resume_parsing", []).append((time.perf_counter() - t0) * 1000)

    t0 = time.perf_counter()
    jd = parse_jd_text(case.job_description_text)
    timings.setdefault("jd_parsing", []).append((time.perf_counter() - t0) * 1000)

    t0 = time.perf_counter()
    breakdown = service.calculate_ats_alignment(jd, resume)
    timings.setdefault("scoring_total", []).append((time.perf_counter() - t0) * 1000)

    requirement_results = []
    for requirement in breakdown.requirements:
        expected_bucket = _expected_bucket_for(case, requirement.text)
        if expected_bucket is None:
            continue
        actual_bucket = _STATUS_TO_BUCKET.get(requirement.status, "unknown")
        requirement_results.append(
            RequirementCaseResult(
                requirement_text=requirement.text,
                expected_bucket=expected_bucket,
                actual_status=requirement.status,
                actual_score=requirement.score,
                correct=(actual_bucket == expected_bucket),
            )
        )

    return CaseResult(
        case_id=case.case_id,
        category=case.category,
        requirement_results=requirement_results,
        all_correct=all(r.correct for r in requirement_results) if requirement_results else False,
        ats_alignment=breakdown.ats_alignment,
    )


def run_evaluation(cases: list[EvaluationCase] | None = None) -> EvaluationReport:
    cases = cases if cases is not None else CASES
    service = ScoringService()
    timings: dict[str, list[float]] = {}

    case_results = [run_case(case, service, timings) for case in cases]

    all_requirement_results = [r for cr in case_results for r in cr.requirement_results]
    matching_metrics = compute_matching_metrics(all_requirement_results)

    false_positives = []
    false_negatives = []
    for case_result in case_results:
        for r in case_result.requirement_results:
            if r.correct:
                continue
            expected_positive = r.expected_bucket == "matches"
            actual_positive = r.actual_status in ("STRONG", "VERY_STRONG")
            if actual_positive and not expected_positive:
                kind = "FALSE_POSITIVE"
            elif expected_positive and not actual_positive:
                kind = "FALSE_NEGATIVE"
            else:
                # Both non-positive but different bucket (e.g. expected
                # "partial", actual "missing") — still a labeling
                # mismatch worth recording, treated as a false negative
                # since the expected condition wasn't met.
                kind = "FALSE_NEGATIVE"
            entry = ErrorAnalysisEntry(
                case_id=case_result.case_id,
                category=case_result.category,
                requirement_text=r.requirement_text,
                expected_bucket=r.expected_bucket,
                actual_status=r.actual_status,
                kind=kind,
            )
            (false_positives if kind == "FALSE_POSITIVE" else false_negatives).append(entry)

    score_statistics = compute_score_statistics([cr.ats_alignment for cr in case_results])

    performance = [
        PerformanceBenchmark(stage=stage, mean_ms=sum(samples) / len(samples), max_ms=max(samples), samples=len(samples))
        for stage, samples in timings.items()
    ]

    return EvaluationReport(
        evaluation_version="EVAL_V1",
        dataset_version=DATASET_VERSION,
        scoring_config_version=get_scoring_config().version,
        cases=len(cases),
        matching_metrics=matching_metrics,
        false_positives=false_positives,
        false_negatives=false_negatives,
        score_statistics=score_statistics,
        performance=performance,
        case_results=case_results,
    )
