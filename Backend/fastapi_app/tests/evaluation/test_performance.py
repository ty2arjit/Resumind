"""Performance baseline (spec Phase 13 §33-34). Establishes a baseline,
not an optimization target — thresholds here are deliberately generous
(catch pathological regressions, e.g. an accidental O(n^2) loop or a
cache that stopped working, not normal variance)."""

from app.modules.evaluation import run_evaluation


def test_performance_benchmark_is_captured_and_bounded():
    report = run_evaluation()
    stages = {p.stage: p for p in report.performance}

    assert "resume_parsing" in stages
    assert "jd_parsing" in stages
    assert "scoring_total" in stages

    for stage in stages.values():
        assert stage.samples == report.cases
        # Generous upper bound: a pathological regression (e.g. an
        # accidentally-uncached embedding reload per call) would blow
        # well past this; normal per-case latency is under 1s.
        assert stage.mean_ms < 5000
