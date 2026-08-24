"""Loads JD-specific configurable vocabulary. Action verbs and technology
keywords are intentionally NOT duplicated here — the job parser imports
those directly from app.modules.resume.vocab (spec §14: "reuse the action
vocabulary/configuration... do not duplicate action dictionaries").
"""

import json
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"


@lru_cache
def get_jd_section_headings() -> dict[str, list[str]]:
    return json.loads((_DATA_DIR / "jd_section_headings.json").read_text())
