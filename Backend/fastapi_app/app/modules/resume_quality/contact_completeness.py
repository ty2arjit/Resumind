"""Contact completeness dimension (spec §9). Rewards useful completeness
rather than heavily penalizing missing optional links — not every role
needs a portfolio/GitHub."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import ContactCompletenessConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_contact_completeness(
    resume: StructuredResume, config: ContactCompletenessConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []
    contact = resume.contact

    core_present = sum(1 for f in (contact.name, contact.email) if f)
    core_score = core_present / 2

    optional_present = sum(1 for f in (contact.phone, contact.linkedin, contact.github, contact.website) if f)
    optional_score = min(1.0, optional_present / config.optional_full_credit_count) if config.optional_full_credit_count else 1.0

    score = config.core_weight * core_score + config.optional_weight * optional_score

    if core_score < 1.0:
        findings.append(
            QualityFinding(
                type=FindingType.CONTACT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="MISSING_CORE_CONTACT_INFO",
                dimension=QualityDimension.CONTACT_COMPLETENESS,
            )
        )

    return max(0.0, min(1.0, score)), findings
