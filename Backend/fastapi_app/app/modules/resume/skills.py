"""Skills section parsing (spec §9).

Most resumes format skills as one category per line:
    "Languages: Python, Java, C++"
    "Frameworks: React, Node.js"
This module splits on that convention where present; a line with no
recognizable category label is bucketed under "other" rather than
discarded.
"""

import re

from app.modules.resume.schemas import SkillCategory

_CATEGORY_MAP = {
    "programming_languages": ["language", "languages", "programming languages"],
    "frameworks": ["framework", "frameworks", "libraries/frameworks"],
    "libraries": ["library", "libraries"],
    "databases": ["database", "databases", "db", "dbms"],
    "cloud": ["cloud", "cloud platforms"],
    "devops": ["devops", "ci/cd", "tools & devops"],
    "tools": ["tools", "software", "developer tools"],
    "concepts": ["concepts", "core concepts", "areas of interest", "coursework"],
}

_LABEL_TO_CATEGORY = {
    label: category for category, labels in _CATEGORY_MAP.items() for label in labels
}

_ITEM_SPLIT_RE = re.compile(r"[,|;/]")


def _split_items(text: str) -> list[str]:
    items = [item.strip(" .") for item in _ITEM_SPLIT_RE.split(text)]
    return [item for item in items if item]


def parse_skills_section(content_lines: list[str]) -> list[SkillCategory]:
    buckets: dict[str, SkillCategory] = {}

    def bucket_for(category: str, raw_label: str | None) -> SkillCategory:
        if category not in buckets:
            buckets[category] = SkillCategory(category=category, category_label=raw_label, items=[])
        return buckets[category]

    for line in content_lines:
        if ":" in line:
            label, rest = line.split(":", 1)
            normalized_label = label.strip().lower()
            category = _LABEL_TO_CATEGORY.get(normalized_label, "other")
            target = bucket_for(category, label.strip() if category == "other" else None)
            target.items.extend(_split_items(rest))
        else:
            target = bucket_for("other", None)
            target.items.extend(_split_items(line))

    return [SkillCategory(category=c.category, category_label=c.category_label, items=_dedupe(c.items)) for c in buckets.values()]


def _dedupe(items: list[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen
