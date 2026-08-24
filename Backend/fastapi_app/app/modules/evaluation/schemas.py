"""Evaluation framework schemas (spec Phase 13 §3, §35-36). Deliberately
separate from production scoring schemas — this module only reads their
outputs, never redefines or reimplements them."""

from pydantic import BaseModel


class ExpectedOutcome(BaseModel):
    """Requirement texts (must match a JD requirement's `text` exactly)
    bucketed by what the evaluator expects the real pipeline to produce.
    `matches` = STRONG/VERY_STRONG, `partial` = PARTIAL/WEAK,
    `missing` = MISSING, `unknown` = UNKNOWN."""

    matches: list[str] = []
    partial: list[str] = []
    missing: list[str] = []
    unknown: list[str] = []
    critical_gaps: list[str] = []


class EvaluationCase(BaseModel):
    case_id: str
    category: str
    description: str
    resume_text: str
    job_description_text: str
    expected: ExpectedOutcome


class RequirementCaseResult(BaseModel):
    requirement_text: str
    expected_bucket: str
    actual_status: str
    actual_score: float
    correct: bool


class CaseResult(BaseModel):
    case_id: str
    category: str
    requirement_results: list[RequirementCaseResult]
    all_correct: bool
    ats_alignment: int


class ConfusionCounts(BaseModel):
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0


class MatchingMetrics(BaseModel):
    """Binary metrics over the "is this requirement satisfied" question
    — positive = expected/actual bucket is STRONG (spec §27)."""

    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    counts: ConfusionCounts = ConfusionCounts()
    bucket_accuracy: float | None = None  # exact 4-way bucket match rate


class ErrorAnalysisEntry(BaseModel):
    case_id: str
    category: str
    requirement_text: str
    expected_bucket: str
    actual_status: str
    kind: str  # "FALSE_POSITIVE" | "FALSE_NEGATIVE"


class ScoreStatistics(BaseModel):
    count: int
    minimum: float
    maximum: float
    mean: float
    near_zero_count: int  # score <= 10
    near_hundred_count: int  # score >= 90


class PerformanceBenchmark(BaseModel):
    stage: str
    mean_ms: float
    max_ms: float
    samples: int


class EvaluationReport(BaseModel):
    evaluation_version: str
    dataset_version: str
    scoring_config_version: str
    cases: int
    matching_metrics: MatchingMetrics
    false_positives: list[ErrorAnalysisEntry] = []
    false_negatives: list[ErrorAnalysisEntry] = []
    score_statistics: ScoreStatistics
    performance: list[PerformanceBenchmark] = []
    case_results: list[CaseResult] = []
