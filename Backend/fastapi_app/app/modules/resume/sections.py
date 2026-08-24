"""Deterministic section detection (spec §3).

The matching algorithm itself lives in app.modules.common.heading_detection
(shared with the JD parser); this module only supplies the resume-specific
canonical types and synonym vocabulary, and resolves each heading into a
content span.
"""

from app.modules.common.heading_detection import build_synonym_index, detect_headings
from app.modules.resume.schemas import CanonicalSection, DetectedSection
from app.modules.resume.vocab import get_section_headings

_SYNONYM_INDEX = build_synonym_index(get_section_headings(), CanonicalSection)


def detect_sections(cleaned_text: str) -> list[DetectedSection]:
    lines = cleaned_text.split("\n")
    matches = detect_headings(lines, _SYNONYM_INDEX, CanonicalSection.OTHER, skip_first_line=True)

    # Resolve each heading's content span: from the line after it to the
    # line before the next detected heading (or end of document).
    resolved: list[DetectedSection] = []
    for idx, match in enumerate(matches):
        next_start = matches[idx + 1].line_index if idx + 1 < len(matches) else len(lines)
        resolved.append(
            DetectedSection(
                canonical_type=match.canonical_type,
                heading_text=match.heading_text,
                confidence=match.confidence,
                start_line=match.line_index,
                end_line=next_start - 1,
            )
        )

    return resolved


def section_content_lines(cleaned_text: str, section: DetectedSection) -> list[str]:
    lines = cleaned_text.split("\n")
    body_start = section.start_line + 1
    body_end = section.end_line + 1
    return [line for line in lines[body_start:body_end] if line.strip()]


def leading_content_lines(cleaned_text: str, sections: list[DetectedSection]) -> list[str]:
    """Lines before the first detected section heading — typically the
    name/contact block, sometimes a short summary."""
    lines = cleaned_text.split("\n")
    end = sections[0].start_line if sections else len(lines)
    return [line for line in lines[:end] if line.strip()]
