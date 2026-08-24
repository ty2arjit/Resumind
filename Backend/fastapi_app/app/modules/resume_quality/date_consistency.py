"""Date consistency dimension (spec §17-18). Never invents a date; an
unparseable date is represented as UNKNOWN (partial credit, not a hard
zero) rather than fabricated. Overlapping experience is not automatically
penalized — students legitimately have concurrent internships/projects."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import DateConsistencyConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_date_consistency(
    resume: StructuredResume, config: DateConsistencyConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    dated_entries = [e.dates for e in (resume.experience + resume.education) if e.dates]
    if not dated_entries:
        return config.no_dates_default_score, findings

    total_score = 0.0
    for date_range in dated_entries:
        entry_score = 1.0

        if date_range.start_text and not date_range.start_normalized:
            entry_score -= config.unparseable_date_penalty
            findings.append(
                QualityFinding(
                    type=FindingType.DATE_SIGNAL,
                    severity=FindingSeverity.LOW,
                    message_key="UNPARSEABLE_DATE",
                    dimension=QualityDimension.DATE_CONSISTENCY,
                )
            )

        if (
            date_range.start_normalized
            and date_range.end_normalized
            and not date_range.is_current
            and date_range.end_normalized < date_range.start_normalized
        ):
            entry_score -= config.invalid_order_penalty
            findings.append(
                QualityFinding(
                    type=FindingType.DATE_SIGNAL,
                    severity=FindingSeverity.MEDIUM,
                    message_key="INVALID_DATE_ORDER",
                    dimension=QualityDimension.DATE_CONSISTENCY,
                )
            )

        total_score += max(0.0, entry_score)

    return max(0.0, min(1.0, total_score / len(dated_entries))), findings
