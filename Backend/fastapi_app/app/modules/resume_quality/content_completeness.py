"""Content completeness dimension (spec §10). Context-sensitive — a
student resume (Education/Projects/Skills) and an experienced-professional
resume (Experience/Skills/Achievements) should both score well."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import ContentCompletenessConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_content_completeness(
    resume: StructuredResume, config: ContentCompletenessConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    categories_present = sum(
        1
        for present in [
            bool(resume.experience),
            bool(resume.projects),
            bool(resume.education),
            bool(resume.skills),
            bool(resume.certifications),
            bool(resume.achievements or resume.leadership),
        ]
        if present
    )
    breadth = categories_present / config.total_category_count

    has_professional_evidence = bool(resume.experience or resume.projects)
    core_signal = 1.0 if has_professional_evidence and resume.skills else (0.6 if resume.skills else 0.4)

    score = 0.6 * core_signal + 0.4 * breadth

    if not has_professional_evidence:
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.HIGH,
                message_key="NO_EXPERIENCE_OR_PROJECTS",
                dimension=QualityDimension.CONTENT_COMPLETENESS,
            )
        )

    return max(0.0, min(1.0, score)), findings
