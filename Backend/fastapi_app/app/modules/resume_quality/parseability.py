"""Parseability dimension (spec §5-6). Whether the resume was
successfully parsed — not whether it's a good resume."""

from app.modules.resume.schemas import ExtractionStatus, StructuredResume
from app.modules.resume_quality.config import ParseabilityConfig
from app.modules.resume_quality.schemas import FindingSeverity, FindingType, QualityDimension, QualityFinding

_WARNING_SEVERITY: dict[str, FindingSeverity] = {
    "empty_document": FindingSeverity.HIGH,
    "possible_scanned_pdf": FindingSeverity.HIGH,
    "low_extracted_text": FindingSeverity.MEDIUM,
    "unsupported_layout": FindingSeverity.MEDIUM,
    "multiple_sections_merged": FindingSeverity.MEDIUM,
    "duplicate_content_removed": FindingSeverity.LOW,
    "ambiguous_section": FindingSeverity.LOW,
    "ambiguous_experience_header": FindingSeverity.LOW,
    "ambiguous_education_entry": FindingSeverity.LOW,
    "malformed_date": FindingSeverity.LOW,
    "missing_expected_section": FindingSeverity.INFO,
}

_EXTRACTION_STATUS_SCORE_ATTR = {
    ExtractionStatus.OK: "ok_score",
    ExtractionStatus.LOW_TEXT: "low_text_score",
    ExtractionStatus.EMPTY: "empty_score",
}


def score_parseability(
    resume: StructuredResume, config: ParseabilityConfig
) -> tuple[float, list[QualityFinding]]:
    findings: list[QualityFinding] = []

    base = getattr(config, _EXTRACTION_STATUS_SCORE_ATTR[resume.document.extraction_status])

    section_count = len({s.canonical_type for s in resume.sections})
    section_score = min(1.0, section_count / config.target_section_count) if config.target_section_count else 1.0

    structural_signals = [1.0 if resume.contact.name or resume.contact.email else 0.5]
    if resume.experience:
        structural_signals.append(
            sum(1 for e in resume.experience if e.organization or e.role) / len(resume.experience)
        )
    if resume.education:
        structural_signals.append(
            sum(1 for e in resume.education if e.institution or e.degree) / len(resume.education)
        )
    signal_score = sum(structural_signals) / len(structural_signals)

    raw = base * 0.5 + section_score * 0.25 + signal_score * 0.25

    penalty = 0.0
    for warning in resume.warnings:
        weight = config.warning_penalty.weights.get(warning.code.value, config.warning_penalty.default_weight)
        penalty += weight
        findings.append(
            QualityFinding(
                type=FindingType.PARSING_WARNING,
                severity=_WARNING_SEVERITY.get(warning.code.value, FindingSeverity.MEDIUM),
                message_key=warning.code.value.upper(),
                dimension=QualityDimension.PARSEABILITY,
            )
        )
    penalty = min(penalty, config.warning_penalty.max_total_penalty)

    score = max(0.0, min(1.0, raw - penalty))
    return score, findings
