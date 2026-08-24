"""Keyword hygiene dimension (spec §19). Flags excessive/suspicious
repetition (near-identical bullets repeated) without punishing legitimate
repetition (e.g. "Python" naturally appearing in Skills, Experience, and
Projects sections)."""

from collections import Counter

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import KeywordHygieneConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding


def score_keyword_hygiene(
    resume: StructuredResume, config: KeywordHygieneConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    texts = [item.text.strip().lower() for item in resume.evidence if item.text.strip()]
    if not texts:
        return config.no_content_score, findings

    counts = Counter(texts)
    duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
    duplicate_ratio = duplicate_count / len(texts)

    score = max(0.0, 1.0 - duplicate_ratio * config.duplicate_penalty_multiplier)

    if duplicate_ratio > config.suspicious_duplicate_threshold:
        findings.append(
            QualityFinding(
                type=FindingType.DUPLICATE_CONTENT,
                severity=FindingSeverity.MEDIUM,
                message_key="EXCESSIVE_REPEATED_CONTENT",
                dimension=QualityDimension.KEYWORD_HYGIENE,
            )
        )

    return max(0.0, min(1.0, score)), findings
