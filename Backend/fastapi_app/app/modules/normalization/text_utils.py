"""Shared text-transformation helpers for the normalization pipeline
(spec §2: "Text Cleaning" -> "Case/Formatting Normalization" stages).
"""

import re

_WHITESPACE_RE = re.compile(r"\s+")
# Only separators are stripped for the formatting key — NOT every
# non-alphanumeric character. Preserving "+" and "#" is what keeps "C",
# "C++", and "C#" from all collapsing onto the same key; only whitespace,
# dots, hyphens, and underscores are treated as pure formatting noise
# ("Node JS" / "Node.js" / "Node-JS" / "Node_JS" all mean the same thing).
_SEPARATOR_RE = re.compile(r"[\s.\-_]+")


def clean_text(raw: str) -> str:
    """Whitespace cleanup only — case and punctuation are untouched here,
    that's the next pipeline stage."""
    return _WHITESPACE_RE.sub(" ", raw.strip())


def normalized_text(raw: str) -> str:
    """Case + whitespace normalized form (spec §16 example:
    raw_value="Postgres" -> normalized_text="postgres")."""
    return clean_text(raw).lower()


def formatting_key(text: str) -> str:
    """Collapses separator punctuation/whitespace so "ReactJS" / "React
    JS" / "React.js" all reduce to the same key, without touching
    symbols that carry real meaning (+, #) or digits (so "Python" and
    "Python3" stay distinct — that pairing needs an explicit alias, not
    an accidental formatting-key collision).
    """
    return _SEPARATOR_RE.sub("", text.lower().strip())
