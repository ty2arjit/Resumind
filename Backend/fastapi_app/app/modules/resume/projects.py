"""Projects section parsing (spec §8).

Simpler than experience parsing: a project entry is usually a single
non-bullet header line (often "Name | tech stack" or "Name — description")
followed by bullets. A new project starts at each non-bullet line rather
than requiring a date, since many project headers have no date at all.
"""

import re

from app.modules.common.bullets import is_bullet, strip_bullet
from app.modules.resume.evidence import build_evidence
from app.modules.resume.schemas import CanonicalSection, Evidence, ProjectEntry
from app.modules.resume.technologies import extract_technologies

_URL_RE = re.compile(r"https?://[^\s)]+")
_HEADER_SPLIT_RE = re.compile(r"\s*[|—–]\s*")


def _split_blocks(content_lines: list[str]) -> list[list[str]]:
    """A new project entry starts at each non-bullet line (its header);
    bullets and any non-bullet description line that follows belong to
    that entry until the next non-bullet header line appears."""
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in content_lines:
        starts_new_entry = not is_bullet(line) and current and any(is_bullet(l) for l in current)
        if starts_new_entry:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)
    return blocks


def parse_projects_section(content_lines: list[str]) -> tuple[list[ProjectEntry], list[Evidence]]:
    entries: list[ProjectEntry] = []
    all_evidence: list[Evidence] = []

    for block in _split_blocks(content_lines):
        header_line = block[0]
        body_lines = block[1:]

        header_parts = [p.strip() for p in _HEADER_SPLIT_RE.split(header_line) if p.strip()]
        name = header_parts[0] if header_parts else header_line.strip()
        header_tech_hint = header_parts[1] if len(header_parts) > 1 else ""

        description = None
        bullets: list[str] = []
        for line in body_lines:
            if is_bullet(line):
                bullets.append(strip_bullet(line))
            elif description is None:
                description = line.strip()
            else:
                bullets.append(line.strip())

        entry_evidence = [
            build_evidence(bullet, CanonicalSection.PROJECTS, position=name) for bullet in bullets
        ]
        all_evidence.extend(entry_evidence)

        links = _URL_RE.findall(" ".join(block))

        technologies: list[str] = []
        for tech in (
            extract_technologies(header_tech_hint)
            + extract_technologies(description or "")
            + [t for ev in entry_evidence for t in ev.technologies]
        ):
            if tech not in technologies:
                technologies.append(tech)

        entries.append(
            ProjectEntry(
                name=name,
                description=description,
                bullets=bullets,
                technologies=technologies,
                links=links,
                raw_header=header_line.strip(),
            )
        )

    return entries, all_evidence
