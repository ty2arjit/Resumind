"""Runs the Phase 13 evaluation dataset through the real pipeline and
asserts the hard safety invariants (spec §43's success criteria) — the
properties that must never regress, regardless of score calibration."""

from app.modules.evaluation import run_evaluation
from app.modules.evaluation.dataset import CASES

_report = run_evaluation()
_case_by_id = {cr.case_id: cr for cr in _report.case_results}


def test_evaluation_covers_the_full_dataset():
    assert _report.cases == len(CASES)
    assert _report.dataset_version == "EVAL_DATASET_V1"


# --- Success criterion: false semantic matches are controlled (spec §43.3) ---
# The single most important safety property in the whole dataset: a
# resume mentioning a DIFFERENT technology must never be classified as a
# strong match for the required one.

def test_distinct_technology_cases_never_produce_a_strong_match():
    distinct_tech_cases = [cr for cr in _report.case_results if cr.category == "DISTINCT_TECHNOLOGY"]
    assert len(distinct_tech_cases) == 4
    for case_result in distinct_tech_cases:
        for requirement in case_result.requirement_results:
            assert requirement.actual_status not in ("STRONG", "VERY_STRONG"), (
                f"{case_result.case_id}: distinct technology incorrectly scored {requirement.actual_status}"
            )


# --- Success criterion: required requirements matter more than preferred (spec §43.5) ---
# Covered directly by tests/unit/scoring/test_requirement_scoring.py's
# importance-weight tests; not duplicated here.

# --- Success criterion: critical requirements have meaningful influence (§43.6) ---

def test_critical_missing_requirement_is_flagged_missing():
    result = _case_by_id["CASE_I1_CRITICAL_MISSING"]
    assert result.requirement_results[0].actual_status == "MISSING"


# --- Success criterion: UNKNOWN differs from MISSING (§43.7) ---

def test_unknown_and_missing_remain_distinguishable():
    unknown_case = _case_by_id["CASE_J1_EXPERIENCE_UNKNOWN_NO_DATES"]
    missing_case = _case_by_id["CASE_Q1_CONFIDENT_ABSENCE_VS_UNKNOWN"]
    assert unknown_case.requirement_results[0].actual_status == "UNKNOWN"
    assert missing_case.requirement_results[0].actual_status == "MISSING"


# --- Reproducibility (spec §13's success criterion; determinism is
# tested more thoroughly in test_determinism.py) ---

def test_evaluation_metrics_are_reproducible():
    second_report = run_evaluation()
    assert second_report.matching_metrics.counts == _report.matching_metrics.counts
    assert second_report.score_statistics.mean == _report.score_statistics.mean
