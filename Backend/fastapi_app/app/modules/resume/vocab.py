"""Loads the configurable vocabularies (action verbs, technology keywords,
section heading synonyms) from app/modules/resume/data/*.json.

Kept as data files rather than inline lists so the vocabulary can be
extended without touching parsing logic (spec §12: "configurable rather
than hardcoded inside parser logic").
"""

import json
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"


@lru_cache
def get_action_verbs() -> list[str]:
    return json.loads((_DATA_DIR / "action_verbs.json").read_text())


@lru_cache
def get_technology_keywords() -> list[str]:
    return json.loads((_DATA_DIR / "technology_keywords.json").read_text())


@lru_cache
def get_section_headings() -> dict[str, list[str]]:
    return json.loads((_DATA_DIR / "section_headings.json").read_text())
