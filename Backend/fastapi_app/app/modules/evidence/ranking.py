"""Evidence ranking (spec §5, §7 — "The Evidence Engine should be
responsible for: selecting, ranking, evaluating, organizing evidence").

Phase 5's raw relevance score alone can rank a bare skills-section
mention above a rich, contextual experience bullet — short exact-phrase
text can score deceptively high on embedding cosine similarity even
though it demonstrates far less (spec §1's own example: "Skills: REST
APIs" is weak evidence, "Experience: Built FastAPI REST APIs..." is
strong). This module is where that evidence-hierarchy correction belongs
— relevance itself (an honest Phase 5 number) is never rewritten, only
the *order* results are returned in.
"""

from app.modules.evidence.schemas import RankedEvidence

_RELEVANCE_WEIGHT = 0.65
_CONTEXT_WEIGHT = 0.35


def _ranking_key(item: RankedEvidence) -> tuple[float, float, str]:
    composite = _RELEVANCE_WEIGHT * item.signals.relevance + _CONTEXT_WEIGHT * item.signals.context_strength
    return (composite, item.signals.relevance, item.evidence_id)


def rank_by_evidence_hierarchy(items: list[RankedEvidence]) -> list[RankedEvidence]:
    return sorted(items, key=_ranking_key, reverse=True)
