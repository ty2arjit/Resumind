from app.modules.matching.exact import exact_signal
from app.modules.matching.schemas import EvidenceContext, MatchableEvidence


def _evidence(technologies):
    return MatchableEvidence(id="ev_1", text="x", context=EvidenceContext.EXPERIENCE, technologies=technologies)


def test_exact_match():
    assert exact_signal(["Python"], _evidence(["Python"])) == 1.0


def test_exact_mismatch():
    assert exact_signal(["Python"], _evidence(["Java"])) == 0.0


def test_no_requirement_technologies_is_not_applicable():
    """None (not 0.0) — 'not applicable' must stay distinguishable from
    'applicable, no match' so fusion doesn't structurally cap
    non-technology requirements (regression: see matching/schemas.py)."""
    assert exact_signal([], _evidence(["Python"])) is None
