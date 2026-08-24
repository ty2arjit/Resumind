"""Section consistency dimension (spec §8). Focuses on machine-readable
structural consistency within a section type — not subjective aesthetics.
E.g. one experience entry has structured dates while another has none."""

from collections.abc import Callable

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import SectionConsistencyConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def _consistency_ratio(entries: list, has_field: Callable) -> float | None:
    if not entries:
        return None
    flags = [bool(has_field(e)) for e in entries]
    true_count = sum(flags)
    return max(true_count, len(flags) - true_count) / len(flags)


def score_section_consistency(
    resume: StructuredResume, config: SectionConsistencyConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []
    ratios: list[tuple[str, float]] = []

    for label, ratio in [
        ("EXPERIENCE_DATES", _consistency_ratio(resume.experience, lambda e: e.dates)),
        ("EDUCATION_DATES", _consistency_ratio(resume.education, lambda e: e.dates)),
        ("PROJECT_TECHNOLOGIES", _consistency_ratio(resume.projects, lambda p: p.technologies)),
    ]:
        if ratio is not None:
            ratios.append((label, ratio))
            if ratio < config.inconsistency_ratio_finding_threshold:
                findings.append(
                    QualityFinding(
                        type=FindingType.STRUCTURE_SIGNAL,
                        severity=FindingSeverity.LOW,
                        message_key=f"INCONSISTENT_{label}",
                        dimension=QualityDimension.SECTION_CONSISTENCY,
                    )
                )

    score = sum(r for _, r in ratios) / len(ratios) if ratios else config.no_entries_default_score
    return max(0.0, min(1.0, score)), findings
