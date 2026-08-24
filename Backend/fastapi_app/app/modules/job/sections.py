"""JD section detection (spec §3). Same engine as the resume parser
(app.modules.common.heading_detection), JD-specific vocabulary/enum.
"""

from app.modules.common.heading_detection import build_synonym_index, detect_headings
from app.modules.job.schemas import JDCanonicalSection, JDDetectedSection
from app.modules.job.vocab import get_jd_section_headings

_SYNONYM_INDEX = build_synonym_index(get_jd_section_headings(), JDCanonicalSection)


def detect_sections(cleaned_text: str) -> list[JDDetectedSection]:
    lines = cleaned_text.split("\n")
    # Line 0 of a JD is very often the job title (e.g. "Backend Software
    # Engineer") — structurally identical to a heading (Title Case, short,
    # no punctuation), so it must be skipped the same way a resume's name
    # line is, or it swallows itself as a bogus first "section" and
    # corrupts metadata extraction's leading-lines lookup.
    matches = detect_headings(lines, _SYNONYM_INDEX, JDCanonicalSection.OTHER, skip_first_line=True)

    resolved: list[JDDetectedSection] = []
    for idx, match in enumerate(matches):
        next_start = matches[idx + 1].line_index if idx + 1 < len(matches) else len(lines)
        resolved.append(
            JDDetectedSection(
                canonical_type=match.canonical_type,
                heading_text=match.heading_text,
                confidence=match.confidence,
                start_line=match.line_index,
                end_line=next_start - 1,
            )
        )

    return resolved


def section_content_lines(cleaned_text: str, section: JDDetectedSection) -> list[str]:
    lines = cleaned_text.split("\n")
    body_start = section.start_line + 1
    body_end = section.end_line + 1
    return [line for line in lines[body_start:body_end] if line.strip()]


def leading_content_lines(cleaned_text: str, sections: list[JDDetectedSection]) -> list[str]:
    lines = cleaned_text.split("\n")
    end = sections[0].start_line if sections else len(lines)
    return [line for line in lines[:end] if line.strip()]
