"""Token-aware keyword/lexical matching (spec §7-8).

Tokenizes on word boundaries specifically so "Java" can never match
inside "JavaScript" as a substring — both become distinct whole tokens
("java" vs "javascript"), and set overlap only counts identical tokens.
"""

import re

_TOKEN_RE = re.compile(r"[a-zA-Z0-9+#]+")
_STOPWORDS = {
    "a", "an", "the", "with", "and", "or", "of", "in", "on", "for", "to",
    "is", "are", "using", "use", "used", "experience", "strong", "skills",
    "knowledge", "years", "year", "will", "you", "your", "we",
}


def _tokenize(text: str) -> set[str]:
    return {
        token.lower()
        for token in _TOKEN_RE.findall(text)
        if len(token) > 1 and token.lower() not in _STOPWORDS
    }


def keyword_signal(requirement_text: str, evidence_text: str) -> tuple[float, list[str]]:
    """Returns (signal, overlapping_tokens). Signal = fraction of the
    requirement's meaningful tokens that also appear in the evidence —
    asymmetric on purpose: a short requirement fully covered by a longer
    evidence bullet should score highly even if the bullet has other
    unrelated tokens too.
    """
    requirement_tokens = _tokenize(requirement_text)
    if not requirement_tokens:
        return 0.0, []

    evidence_tokens = _tokenize(evidence_text)
    overlap = requirement_tokens & evidence_tokens
    signal = len(overlap) / len(requirement_tokens)
    return min(signal, 1.0), sorted(overlap)
