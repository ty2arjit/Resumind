"""Structure dimension (spec §7). Rewards coherent structure without
requiring one rigid template — a research resume may legitimately lack
a Projects section."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import StructureConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_structure(resume: StructuredResume, config: StructureConfig) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    present_types = {s.canonical_type for s in resume.sections}
    breadth = min(1.0, len(present_types) / config.target_section_breadth) if config.target_section_breadth else 1.0

    coherence_signals = []
    if resume.experience:
        coherence_signals.append(sum(1 for e in resume.experience if e.dates or e.bullets) / len(resume.experience))
    if resume.education:
        coherence_signals.append(sum(1 for e in resume.education if e.degree or e.institution) / len(resume.education))
    if resume.projects:
        coherence_signals.append(sum(1 for p in resume.projects if p.name) / len(resume.projects))
    if resume.skills:
        coherence_signals.append(1.0 if any(sc.items for sc in resume.skills) else 0.5)

    coherence = (
        sum(coherence_signals) / len(coherence_signals) if coherence_signals else config.no_content_coherence_score
    )

    score = 0.6 * coherence + 0.4 * breadth

    if breadth < 1 / max(config.target_section_breadth, 1):
        findings.append(
            QualityFinding(
                type=FindingType.STRUCTURE_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="FEW_SECTIONS_DETECTED",
                dimension=QualityDimension.STRUCTURE,
            )
        )

    return max(0.0, min(1.0, score)), findings
