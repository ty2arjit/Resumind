"""ATS Evaluation, Validation & Calibration framework (spec Phase 13).

A controlled internal benchmark for the Resumind ATS pipeline — NOT a
claim of real-world validation, hiring-outcome prediction, or parity
with commercial ATS systems (spec §4, §39-40). Read-only with respect to
production parsing/matching/scoring: this module only measures behavior,
it never changes it.
"""

from app.modules.evaluation.dataset import CASES, DATASET_VERSION
from app.modules.evaluation.runner import run_evaluation
from app.modules.evaluation.schemas import EvaluationCase, EvaluationReport, ExpectedOutcome

__all__ = ["CASES", "DATASET_VERSION", "run_evaluation", "EvaluationCase", "EvaluationReport", "ExpectedOutcome"]
