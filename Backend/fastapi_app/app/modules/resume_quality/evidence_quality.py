"""Evidence quality dimension (spec §13-16). Uses Phase 2's structured
evidence decomposition (action/object/technology/metric). Metrics are a
quality signal, not a mandatory requirement — a bullet missing one is not
penalized to zero."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import EvidenceQualityConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding

_COMPONENTS = 4  # action, technology, object, metric


def score_evidence_quality(
    resume: StructuredResume, config: EvidenceQualityConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []
    evidence = resume.evidence

    if not evidence:
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="NO_STRUCTURED_EVIDENCE",
                dimension=QualityDimension.EVIDENCE_QUALITY,
            )
        )
        return config.no_evidence_score, findings

    per_bullet_scores = []
    metric_count = 0
    action_count = 0
    for item in evidence:
        present = sum(
            1
            for component in (item.actions, item.technologies, item.objects, item.metrics)
            if component
        )
        per_bullet_scores.append(present / _COMPONENTS)
        if item.metrics:
            metric_count += 1
        if item.actions:
            action_count += 1

    avg_score = sum(per_bullet_scores) / len(per_bullet_scores)
    metric_ratio = metric_count / len(evidence)
    action_ratio = action_count / len(evidence)

    if metric_ratio < config.low_metric_ratio_threshold:
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="FEW_MEASURABLE_RESULTS",
                dimension=QualityDimension.EVIDENCE_QUALITY,
            )
        )
    if action_ratio < config.low_action_ratio_threshold:
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="FEW_ACTION_VERBS",
                dimension=QualityDimension.EVIDENCE_QUALITY,
            )
        )

    return max(0.0, min(1.0, avg_score)), findings
