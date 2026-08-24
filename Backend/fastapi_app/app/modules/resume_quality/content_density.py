"""Content density dimension (spec §20). Only scores signals reliably
measurable from extracted text — no subjective visual/layout claims.
Neither a two-page nor a two-column resume is penalized by itself."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import ContentDensityConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_content_density(
    resume: StructuredResume, config: ContentDensityConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    bullets = [b for entry in resume.experience for b in entry.bullets] + [
        b for project in resume.projects for b in project.bullets
    ]
    if not bullets:
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="NO_BULLET_CONTENT",
                dimension=QualityDimension.CONTENT_DENSITY,
            )
        )
        return config.no_bullets_score, findings

    lengths = [len(b.split()) for b in bullets]
    avg_len = sum(lengths) / len(lengths)

    if avg_len < config.min_ideal_words:
        score = max(0.3, avg_len / config.min_ideal_words)
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.LOW,
                message_key="BULLETS_TOO_SHORT",
                dimension=QualityDimension.CONTENT_DENSITY,
            )
        )
    elif avg_len > config.max_ideal_words:
        excess = avg_len - config.max_ideal_words
        score = max(0.3, 1.0 - excess / config.max_ideal_words)
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.LOW,
                message_key="BULLETS_TOO_LONG",
                dimension=QualityDimension.CONTENT_DENSITY,
            )
        )
    else:
        score = 1.0

    text_word_count = len(resume.document.cleaned_text.split())
    page_count = resume.document.page_count or 1
    words_per_page = text_word_count / page_count

    if words_per_page < config.min_words_per_page:
        score = min(score, config.sparse_content_score_cap)
        findings.append(
            QualityFinding(
                type=FindingType.CONTENT_SIGNAL,
                severity=FindingSeverity.MEDIUM,
                message_key="SPARSE_CONTENT",
                dimension=QualityDimension.CONTENT_DENSITY,
            )
        )

    return max(0.0, min(1.0, score)), findings
