"""JD parsing orchestrator (spec §21).

Reuses the resume parser's document extraction and text cleaning wholesale
(spec §1-2: "reuse... do not duplicate document extraction logic") — only
section detection, metadata, and requirement extraction are JD-specific.
Calls no LLM anywhere in this module (spec §26).
"""

from app.modules.job.experience_requirements import extract_experience_requirement
from app.modules.job.metadata import extract_metadata
from app.modules.job.qualifications import build_qualifications
from app.modules.job.requirements import (
    NON_REQUIREMENT_SECTIONS,
    build_requirement,
    find_duplicate_groups,
    split_candidate_sentences,
)
from app.modules.job.responsibilities import build_responsibilities
from app.modules.job.schemas import (
    JDCanonicalSection,
    JDDocumentFormat,
    JDDocumentMeta,
    JDParsingWarning,
    JDWarningCode,
    Requirement,
    StructuredJD,
)
from app.modules.job.sections import detect_sections, leading_content_lines, section_content_lines
from app.modules.resume.clean import clean_text
from app.modules.resume.extract_document import extract_docx, extract_pdf
from app.modules.resume.schemas import ExtractionStatus
from app.modules.resume.technologies import extract_technologies

_EXPECTED_SECTIONS = {JDCanonicalSection.RESPONSIBILITIES, JDCanonicalSection.QUALIFICATIONS_REQUIRED}


def parse_pdf_bytes(file_bytes: bytes) -> StructuredJD:
    extraction = extract_pdf(file_bytes)
    return _parse(
        format=JDDocumentFormat.PDF,
        page_count=extraction.page_count,
        raw_text=extraction.raw_text,
        pages=extraction.pages,
        extraction_status=extraction.extraction_status,
    )


def parse_docx_bytes(file_bytes: bytes) -> StructuredJD:
    extraction = extract_docx(file_bytes)
    return _parse(
        format=JDDocumentFormat.DOCX,
        page_count=None,
        raw_text=extraction.raw_text,
        pages=extraction.pages,
        extraction_status=extraction.extraction_status,
    )


def parse_text(text: str) -> StructuredJD:
    """JD supplied directly as pasted/typed text (spec §1) — there is no
    extraction step to fail, so status is only ever OK or EMPTY, never
    "possibly scanned"."""
    status = ExtractionStatus.OK if text.strip() else ExtractionStatus.EMPTY
    return _parse(format=JDDocumentFormat.TEXT, page_count=None, raw_text=text, pages=[text], extraction_status=status)


def _parse(
    format: JDDocumentFormat,
    page_count: int | None,
    raw_text: str,
    pages: list[str],
    extraction_status: ExtractionStatus,
) -> StructuredJD:
    warnings: list[JDParsingWarning] = []

    if extraction_status == ExtractionStatus.EMPTY:
        warnings.append(JDParsingWarning(code=JDWarningCode.EMPTY_DOCUMENT, message="No text could be extracted from the document."))
    elif extraction_status == ExtractionStatus.LOW_TEXT:
        warnings.append(
            JDParsingWarning(
                code=JDWarningCode.LOW_EXTRACTED_TEXT,
                message="Very little text was extracted relative to the document's length — it may be a scanned/image-based document.",
            )
        )
        warnings.append(
            JDParsingWarning(code=JDWarningCode.POSSIBLE_SCANNED_PDF, message="This document may be image-based; OCR is not performed in this phase.")
        )

    cleaned_text = clean_text(raw_text, pages if format != JDDocumentFormat.TEXT else None)
    document = JDDocumentMeta(
        format=format, page_count=page_count, raw_text=raw_text, cleaned_text=cleaned_text, extraction_status=extraction_status
    )

    if not cleaned_text.strip():
        return StructuredJD(document=document, warnings=warnings)

    sections = detect_sections(cleaned_text)
    leading_lines = leading_content_lines(cleaned_text, sections)
    metadata = extract_metadata(cleaned_text, leading_lines)

    requirements: list[Requirement] = []
    counter = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"req_{counter:03d}"

    def extract_from(lines: list[str], section: JDCanonicalSection | None) -> None:
        nonlocal requirements
        for candidate in split_candidate_sentences(lines):
            req = build_requirement(candidate, section or JDCanonicalSection.OTHER, next_id())
            if req is not None:
                requirements.append(req)

    if sections:
        for section in sections:
            if section.canonical_type in NON_REQUIREMENT_SECTIONS:
                continue
            extract_from(section_content_lines(cleaned_text, section), section.canonical_type)
    else:
        # No headings detected at all — common for a short plain-text JD
        # (spec §24 test case 11). Scan the whole document as one
        # unsectioned block rather than silently producing nothing.
        extract_from(cleaned_text.split("\n"), None)

    duplicate_groups = find_duplicate_groups(requirements)
    for group in duplicate_groups:
        texts = ", ".join(repr(r.text) for r in group)
        warnings.append(
            JDParsingWarning(code=JDWarningCode.DUPLICATE_REQUIREMENTS, message=f"Possible duplicate requirements: {texts}")
        )

    for req in requirements:
        # RESPONSIBILITY items have no inherent required/preferred
        # semantics, so UNKNOWN there is the expected steady state, not a
        # signal worth a warning — only flag it for requirement types
        # where importance is actually meaningful.
        if req.type.value == "RESPONSIBILITY":
            continue
        # UNKNOWN importance IS the ambiguity signal (spec §18) — it's not
        # additionally gated on a confidence threshold, since a concrete
        # technology/entity match already pushes confidence past a
        # threshold like 0.6 even when the importance itself is unresolved.
        if req.importance.value == "UNKNOWN":
            warnings.append(
                JDParsingWarning(
                    code=JDWarningCode.LOW_CONFIDENCE_CLASSIFICATION,
                    message=f"Low-confidence classification for requirement: {req.text!r}",
                    section=req.source_section,
                )
            )

    skills = []
    for tech in extract_technologies(cleaned_text):
        if tech not in skills:
            skills.append(tech)

    experience_requirements = [req.experience for req in requirements if req.experience is not None]

    detected_types = {s.canonical_type for s in sections}
    for expected in _EXPECTED_SECTIONS:
        if expected not in detected_types:
            warnings.append(
                JDParsingWarning(
                    code=JDWarningCode.MISSING_EXPECTED_SECTION,
                    message=f"No {expected.value} section was detected.",
                    section=expected,
                )
            )

    return StructuredJD(
        document=document,
        metadata=metadata,
        sections=sections,
        requirements=requirements,
        responsibilities=build_responsibilities(requirements),
        skills=skills,
        qualifications=build_qualifications(requirements),
        experience_requirements=experience_requirements,
        warnings=warnings,
    )
