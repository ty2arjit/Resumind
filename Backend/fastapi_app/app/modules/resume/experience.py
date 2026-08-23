"""Experience section parsing (spec §7).

Entry headers are found by locating lines that contain a date range —
virtually every experience entry has one on its header line. Splitting a
header into role/organization is inherently ambiguous in free text (both
"Role, Organization" and "Organization, Role" are common); when the split
can't be done confidently, raw_header is preserved and a warning is
raised rather than guessing.
"""

import re

from app.modules.common.bullets import is_bullet, strip_bullet
from app.modules.resume.dates import extract_date_range
from app.modules.resume.evidence import build_evidence
from app.modules.resume.schemas import CanonicalSection, Evidence, ExperienceEntry
from app.modules.resume.technologies import extract_technologies

_HEADER_SPLIT_RE = re.compile(r"\s*[|,–—]\s*|\s+at\s+", re.IGNORECASE)
_DATE_TOKEN_RE = re.compile(
    r"(?:[A-Za-z]{3,9}\.?\s+\d{4}|\d{1,2}[/-]\d{4}|\d{4})\s*(?:-|–|—|to)\s*"
    r"(?:present|current|[A-Za-z]{3,9}\.?\s+\d{4}|\d{1,2}[/-]\d{4}|\d{4})",
    re.IGNORECASE,
)


def _looks_like_header(line: str) -> bool:
    if is_bullet(line):
        return False
    return bool(_DATE_TOKEN_RE.search(line))


def _date_range_match(line: str) -> re.Match | None:
    return _DATE_TOKEN_RE.search(line)


def _is_pure_date_line(line: str) -> bool:
    """True if the line is nothing but a date range (e.g. "Jun 2023 - Aug
    2023" on its own line) — the common two-line header pattern where the
    role/organization is on the line above."""
    match = _date_range_match(line)
    if not match:
        return False
    remainder = (line[: match.start()] + line[match.end() :]).strip(" -|,–—:")
    return remainder == ""


def _merge_two_line_headers(content_lines: list[str]) -> list[str]:
    """Combines a plain "Role, Organization" line immediately followed by
    a pure-date-range line into a single header line, so the rest of the
    pipeline only ever has to deal with one header shape."""
    merged: list[str] = []
    i = 0
    n = len(content_lines)
    while i < n:
        line = content_lines[i]
        has_next = i + 1 < n
        if (
            has_next
            and not is_bullet(line)
            and not _looks_like_header(line)
            and line.strip()
            and _is_pure_date_line(content_lines[i + 1])
        ):
            merged.append(f"{line.strip()}  {content_lines[i + 1].strip()}")
            i += 2
            continue
        merged.append(line)
        i += 1
    return merged


def _split_blocks(content_lines: list[str]) -> list[list[str]]:
    """Groups lines into one block per experience entry, each starting at
    a header line (a non-bullet line carrying a date range)."""
    lines = _merge_two_line_headers(content_lines)
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if _looks_like_header(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)
    return blocks


def _split_header(header_without_dates: str) -> tuple[str | None, str | None]:
    """Best-effort split of "Role, Organization" / "Role | Organization"
    style headers. Returns (role, organization); either may be None if the
    header can't be confidently split."""
    parts = [p.strip() for p in _HEADER_SPLIT_RE.split(header_without_dates) if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


def parse_experience_section(content_lines: list[str]) -> tuple[list[ExperienceEntry], list[Evidence], list[str]]:
    entries: list[ExperienceEntry] = []
    all_evidence: list[Evidence] = []
    warnings: list[str] = []

    for block in _split_blocks(content_lines):
        header_line = block[0]
        body_lines = block[1:]

        dates = extract_date_range(header_line)
        header_without_dates = header_line
        date_match = _date_range_match(header_line)
        if date_match:
            header_without_dates = header_line[: date_match.start()] + header_line[date_match.end() :]
            header_without_dates = header_without_dates.strip(" -|,–—:")

        role, organization = _split_header(header_without_dates)
        if role is None:
            warnings.append(f"Could not confidently split experience header: {header_line!r}")

        bullets: list[str] = []
        for line in body_lines:
            text = strip_bullet(line) if is_bullet(line) else line.strip()
            if not text:
                continue
            bullets.append(text)

        entry_evidence = [
            build_evidence(bullet, CanonicalSection.EXPERIENCE, position=role or header_without_dates)
            for bullet in bullets
        ]
        all_evidence.extend(entry_evidence)

        technologies: list[str] = []
        for tech in extract_technologies(header_without_dates) + [t for ev in entry_evidence for t in ev.technologies]:
            if tech not in technologies:
                technologies.append(tech)

        entries.append(
            ExperienceEntry(
                organization=organization,
                role=role,
                location=None,
                dates=dates,
                bullets=bullets,
                technologies=technologies,
                raw_header=header_line.strip(),
            )
        )

    return entries, all_evidence, warnings
