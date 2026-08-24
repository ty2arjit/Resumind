"""Education section parsing (spec §6)."""

import re

from app.modules.resume.dates import extract_date_range
from app.modules.resume.schemas import EducationEntry

_DEGREE_RE = re.compile(
    r"\b(B\.?\s?Tech|M\.?\s?Tech|B\.?\s?E|M\.?\s?E|Bachelor(?:'?s)?|Master(?:'?s)?|"
    r"B\.?\s?Sc|M\.?\s?Sc|Ph\.?\s?D|Doctorate|Diploma|MBA|BBA|BCA|MCA|"
    r"Higher Secondary|Senior Secondary|12th|10th)\b",
    re.IGNORECASE,
)
_INSTITUTION_KEYWORDS_RE = re.compile(
    r"\b(University|College|Institute|Institution|School|Academy|Polytechnic)\b",
    re.IGNORECASE,
)
_GPA_RE = re.compile(r"\b(?:CGPA|GPA)\s*[:\-]?\s*(\d(?:\.\d+)?)\s*(?:/\s*(\d(?:\.\d+)?))?", re.IGNORECASE)
_PERCENTAGE_RE = re.compile(r"\b(\d{2,3}(?:\.\d+)?)\s*%")
_FIELD_RE = re.compile(
    r"\b(?:in|of)\s+([A-Za-z][A-Za-z &,\-]{2,60})", re.IGNORECASE
)


def _split_into_blocks(content_lines: list[str]) -> list[list[str]]:
    """Groups lines into one block per education entry. A new block starts
    only at an institution-keyword line: institution and degree are very
    often on separate lines for the same entry ("NIT Rourkela" / "B.Tech
    in Computer Science, 2020 - 2024"), so splitting on degree keywords
    too would tear one entry into two.
    """
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in content_lines:
        starts_new = bool(_INSTITUTION_KEYWORDS_RE.search(line))
        if starts_new and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)
    return blocks


def parse_education_section(content_lines: list[str]) -> list[EducationEntry]:
    entries: list[EducationEntry] = []

    for block in _split_into_blocks(content_lines):
        block_text = " ".join(block)

        institution = None
        for line in block:
            if _INSTITUTION_KEYWORDS_RE.search(line):
                institution = line.strip()
                break
        if institution is None and block:
            # Institution names that are proper-noun abbreviations (e.g.
            # "NIT Rourkela", "IIT Bombay") won't match the keyword list;
            # the first line of an education entry is institution far more
            # often than not, so it's a reasonable fallback rather than
            # leaving this consistently empty for such entries.
            institution = block[0].strip()

        degree_match = _DEGREE_RE.search(block_text)
        degree = degree_match.group(0).strip() if degree_match else None

        field = None
        field_match = _FIELD_RE.search(block_text)
        if field_match:
            field = field_match.group(1).strip(" .,")

        gpa = None
        gpa_match = _GPA_RE.search(block_text)
        if gpa_match:
            gpa = gpa_match.group(1)

        percentage = None
        percentage_match = _PERCENTAGE_RE.search(block_text)
        if percentage_match:
            percentage = f"{percentage_match.group(1)}%"

        dates = extract_date_range(block_text)

        entries.append(
            EducationEntry(
                institution=institution,
                degree=degree,
                field=field,
                dates=dates,
                gpa=gpa,
                percentage=percentage,
                coursework=[],
                raw_text=block_text.strip(),
            )
        )

    return entries
