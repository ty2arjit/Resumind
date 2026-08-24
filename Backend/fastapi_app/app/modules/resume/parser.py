"""Resume parsing orchestrator (spec §19).

parse_pdf_bytes / parse_docx_bytes are the module's public entry points —
everything else in app/modules/resume is an implementation detail wired
together here. This module does not call Gemini or any LLM (spec §22) and
does not decide whether the resume satisfies any requirement (spec §20) —
it only describes what the resume contains.
"""

from app.modules.resume.contact import extract_contact
from app.modules.resume.education import parse_education_section
from app.modules.resume.experience import parse_experience_section
from app.modules.resume.extract_document import DocumentExtraction, extract_docx, extract_pdf
from app.modules.resume.clean import clean_text
from app.modules.resume.projects import parse_projects_section
from app.modules.resume.schemas import (
    CanonicalSection,
    ContactInfo,
    DocumentMeta,
    ExtractionStatus,
    ParsingWarning,
    StructuredResume,
    WarningCode,
)
from app.modules.resume.sections import detect_sections, leading_content_lines, section_content_lines
from app.modules.resume.skills import parse_skills_section

_RAW_TEXT_SECTIONS = {
    CanonicalSection.CERTIFICATIONS: "certifications",
    CanonicalSection.ACHIEVEMENTS: "achievements",
    CanonicalSection.LEADERSHIP: "leadership",
    CanonicalSection.EXTRACURRICULAR: "extracurriculars",
    CanonicalSection.PUBLICATIONS: "publications",
    CanonicalSection.INTERESTS: "interests",
}

_EXPECTED_SECTIONS = {CanonicalSection.EDUCATION, CanonicalSection.EXPERIENCE, CanonicalSection.SKILLS}


def parse_pdf_bytes(file_bytes: bytes) -> StructuredResume:
    return _parse(extract_pdf(file_bytes))


def parse_docx_bytes(file_bytes: bytes) -> StructuredResume:
    return _parse(extract_docx(file_bytes))


def _parse(extraction: DocumentExtraction) -> StructuredResume:
    warnings: list[ParsingWarning] = []

    if extraction.extraction_status == ExtractionStatus.EMPTY:
        warnings.append(ParsingWarning(code=WarningCode.EMPTY_DOCUMENT, message="No text could be extracted from the document."))
    elif extraction.extraction_status == ExtractionStatus.LOW_TEXT:
        warnings.append(
            ParsingWarning(
                code=WarningCode.LOW_EXTRACTED_TEXT,
                message="Very little text was extracted relative to the document's length — it may be a scanned/image-based document.",
            )
        )
        warnings.append(
            ParsingWarning(code=WarningCode.POSSIBLE_SCANNED_PDF, message="This document may be image-based; OCR is not performed in this phase.")
        )

    cleaned_text = clean_text(extraction.raw_text, extraction.pages)
    document = DocumentMeta(
        format=extraction.format,
        page_count=extraction.page_count,
        raw_text=extraction.raw_text,
        cleaned_text=cleaned_text,
        extraction_status=extraction.extraction_status,
    )

    if not cleaned_text.strip():
        return StructuredResume(document=document, contact=ContactInfo(), warnings=warnings)

    sections = detect_sections(cleaned_text)
    leading_lines = leading_content_lines(cleaned_text, sections)
    contact = extract_contact(cleaned_text, leading_lines)

    resume = StructuredResume(document=document, sections=sections, contact=contact)

    sections_by_type: dict[CanonicalSection, list] = {}
    for section in sections:
        sections_by_type.setdefault(section.canonical_type, []).append(section)
        if len(sections_by_type[section.canonical_type]) > 1:
            warnings.append(
                ParsingWarning(
                    code=WarningCode.MULTIPLE_SECTIONS_MERGED,
                    message=f"Multiple headings detected for {section.canonical_type.value}; content was merged.",
                    section=section.canonical_type,
                )
            )

    def content_for(canonical: CanonicalSection) -> list[str]:
        lines: list[str] = []
        for section in sections_by_type.get(canonical, []):
            lines.extend(section_content_lines(cleaned_text, section))
        return lines

    summary_lines = content_for(CanonicalSection.SUMMARY)
    if summary_lines:
        resume.summary = " ".join(summary_lines)

    resume.education = parse_education_section(content_for(CanonicalSection.EDUCATION))

    experience_entries, experience_evidence, experience_warnings = parse_experience_section(
        content_for(CanonicalSection.EXPERIENCE)
    )
    resume.experience = experience_entries
    for message in experience_warnings:
        warnings.append(ParsingWarning(code=WarningCode.AMBIGUOUS_SECTION, message=message, section=CanonicalSection.EXPERIENCE))

    project_entries, project_evidence = parse_projects_section(content_for(CanonicalSection.PROJECTS))
    resume.projects = project_entries

    resume.skills = parse_skills_section(content_for(CanonicalSection.SKILLS))

    for canonical, field_name in _RAW_TEXT_SECTIONS.items():
        lines = content_for(canonical)
        if lines:
            setattr(resume, field_name, lines)

    resume.evidence = experience_evidence + project_evidence

    detected_types = set(sections_by_type.keys())
    for expected in _EXPECTED_SECTIONS:
        if expected not in detected_types:
            warnings.append(
                ParsingWarning(
                    code=WarningCode.MISSING_EXPECTED_SECTION,
                    message=f"No {expected.value} section was detected.",
                    section=expected,
                )
            )

    resume.warnings = warnings
    return resume
