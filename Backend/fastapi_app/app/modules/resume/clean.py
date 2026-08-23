"""Deterministic text cleaning (spec §2).

raw_text is never mutated — this module only ever produces a derived
cleaned_text, so the original extraction is always available for
debugging/audit.
"""

import re

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_BLANK_LINE_RE = re.compile(r"\n{3,}")
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")
_PAGE_NUMBER_LINE_RE = re.compile(r"^\s*(page\s+)?\d{1,3}(\s*/\s*\d{1,3})?(\s+of\s+\d{1,3})?\s*$", re.IGNORECASE)


def clean_text(raw_text: str, pages: list[str] | None = None) -> str:
    text = raw_text.replace("\f", "\n")
    text = _CONTROL_CHARS_RE.sub("", text)

    # De-hyphenate line-wrap artifacts: "informa-\ntion" -> "information".
    text = _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)

    lines = text.split("\n")
    lines = _drop_repeated_header_footer_lines(lines, pages)
    lines = [line for line in lines if not _PAGE_NUMBER_LINE_RE.match(line)]
    lines = _collapse_adjacent_duplicate_lines(lines)

    text = "\n".join(lines)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_BLANK_LINE_RE.sub("\n\n", text)
    return text.strip()


def _drop_repeated_header_footer_lines(lines: list[str], pages: list[str] | None) -> list[str]:
    """Removes lines that repeat verbatim as the first/last non-empty line
    of two or more pages (typical running headers/footers), keeping the
    first occurrence only.
    """
    if not pages or len(pages) < 2:
        return lines

    edge_line_counts: dict[str, int] = {}
    for page_text in pages:
        page_lines = [l.strip() for l in page_text.split("\n") if l.strip()]
        if not page_lines:
            continue
        for edge in (page_lines[0], page_lines[-1]):
            if len(edge) >= 4:  # ignore trivial short lines (e.g. bullets)
                edge_line_counts[edge] = edge_line_counts.get(edge, 0) + 1

    repeated = {line for line, count in edge_line_counts.items() if count >= 2}
    if not repeated:
        return lines

    result = []
    seen_once = set()
    for line in lines:
        stripped = line.strip()
        if stripped in repeated:
            if stripped in seen_once:
                continue  # drop the repeat
            seen_once.add(stripped)
        result.append(line)
    return result


def _collapse_adjacent_duplicate_lines(lines: list[str]) -> list[str]:
    """Collapses a non-trivial line immediately duplicated by extraction
    (e.g. overlapping text blocks) into a single occurrence."""
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if (
            result
            and stripped
            and len(stripped) > 15
            and result[-1].strip() == stripped
        ):
            continue
        result.append(line)
    return result
