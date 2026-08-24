"""Job metadata extraction (spec §4).

Deterministic and conservative: explicit "Label: value" lines are the
primary signal; the only unlabeled fallback is the job title (often the
document's first line, mirroring how a resume's name is usually its first
line). Everything else stays None rather than guessed.
"""

import re

from app.modules.job.schemas import JobMetadata

_LABEL_RE = re.compile(
    r"^(job title|position|role|company|employer|location|employment type|"
    r"job type|experience|department|team)\s*:\s*(.+)$",
    re.IGNORECASE,
)

_EMPLOYMENT_TYPE_RE = re.compile(
    r"\b(full[\s-]?time|part[\s-]?time|contract|internship|freelance|temporary)\b",
    re.IGNORECASE,
)
_WORK_MODE_RE = re.compile(r"\b(remote|hybrid|on[\s-]?site|in[\s-]office)\b", re.IGNORECASE)
_EXPERIENCE_HINT_RE = re.compile(r"\b\d+\+?\s*(?:-|to)?\s*\d*\+?\s*years?\b", re.IGNORECASE)

_TITLE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9./&'\-]*(?:\s+[A-Za-z0-9./&'\-]+){0,6}$")


def _looks_like_title(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return False
    if stripped.endswith((".", ",")):
        return False
    if not _TITLE_NAME_RE.match(stripped):
        return False
    # A job title is Title Case ("Backend Software Engineer"); an
    # ordinary sentence ("we are hiring for a great role") would otherwise
    # also satisfy the character-class/length checks above.
    words = stripped.split()
    return all(word[0].isupper() for word in words if word[0].isalpha())


def extract_metadata(full_text: str, leading_lines: list[str]) -> JobMetadata:
    metadata = JobMetadata()
    label_map = {
        "job title": "title",
        "position": "title",
        "role": "title",
        "company": "company",
        "employer": "company",
        "location": "location",
        "employment type": "employment_type",
        "job type": "employment_type",
        "experience": "experience",
        "department": "department",
        "team": "department",
    }

    for line in full_text.split("\n"):
        match = _LABEL_RE.match(line.strip())
        if not match:
            continue
        label = match.group(1).lower()
        value = match.group(2).strip()
        field = label_map[label]
        if getattr(metadata, field) is None:
            setattr(metadata, field, value)

    if metadata.title is None:
        for line in leading_lines[:2]:
            if _looks_like_title(line):
                metadata.title = line.strip()
                break

    if metadata.employment_type is None:
        match = _EMPLOYMENT_TYPE_RE.search(full_text)
        if match:
            metadata.employment_type = match.group(0)

    work_mode_match = _WORK_MODE_RE.search(full_text)
    if work_mode_match:
        metadata.work_mode = work_mode_match.group(0)

    if metadata.experience is None:
        match = _EXPERIENCE_HINT_RE.search(full_text)
        if match:
            metadata.experience = match.group(0).strip()

    return metadata
