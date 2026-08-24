"""Exercises the full MatchingService, including the real local
embedding model (spec §30) — slower than the pure-signal tests, but this
is what actually proves end-to-end protection against false positives.
"""

from app.models.enums import MatchStrength
from app.modules.matching.schemas import EvidenceContext, MatchableEvidence
from app.modules.matching.service import MatchingService

_service = MatchingService()


def _evidence(text, technologies=None, actions=None, context=EvidenceContext.EXPERIENCE, id="ev_001"):
    return MatchableEvidence(id=id, text=text, context=context, technologies=technologies or [], actions=actions or [])


def test_exact_match_produces_strong_signal():
    result = _service.match_evidence("req_1", "Python", ["Python"], _evidence("Python", ["Python"]))
    assert result.signals.exact == 1.0
    assert result.match_type in (MatchStrength.STRONG, MatchStrength.VERY_STRONG)


def test_canonical_match_produces_full_canonical_signal():
    result = _service.match_evidence(
        "req_1", "Experience with PostgreSQL", ["PostgreSQL"], _evidence("Worked with Postgres", ["Postgres"])
    )
    assert result.signals.canonical == 1.0
    assert result.explanation.canonical_entity_match is True


def test_docker_kubernetes_never_becomes_a_strong_match():
    result = _service.match_evidence(
        "req_1", "Kubernetes", ["Kubernetes"], _evidence("Deployed services using Docker containers", ["Docker"])
    )
    assert result.match_type in (MatchStrength.MISSING, MatchStrength.WEAK)
    assert result.signals.canonical == 0.0


def test_java_never_matches_javascript():
    result = _service.match_evidence(
        "req_1", "Java", ["Java"], _evidence("Built frontend apps using JavaScript", ["JavaScript"])
    )
    assert result.match_type in (MatchStrength.MISSING, MatchStrength.WEAK)


def test_react_and_react_native_stay_distinct():
    result = _service.match_evidence(
        "req_1", "React", ["React"], _evidence("Built mobile apps with React Native", ["React Native"])
    )
    assert result.signals.canonical == 0.0
    assert result.match_type in (MatchStrength.MISSING, MatchStrength.WEAK)


def test_responsibility_semantic_signal_is_meaningful():
    result = _service.match_evidence(
        "req_1", "Develop REST APIs", [], _evidence("Built FastAPI REST services handling 10K requests/day", ["FastAPI"])
    )
    assert result.signals.exact is None  # not applicable — no requirement technology
    assert result.signals.semantic is not None and result.signals.semantic > 0.2


def test_weak_semantic_relation_does_not_become_technology_equivalence():
    """spec §30: 'Kubernetes' vs 'Container orchestration' may have some
    semantic relation, but must not become exact technology equivalence."""
    result = _service.match_evidence("req_1", "Kubernetes", ["Kubernetes"], _evidence("Container orchestration platform"))
    assert result.signals.canonical == 0.0
    assert result.signals.exact == 0.0


def test_insufficient_evidence_is_missing_not_fabricated():
    result = _service.match_evidence(
        "req_1", "Kubernetes orchestration", ["Kubernetes"], _evidence("Unrelated bullet about marketing analytics")
    )
    assert result.match_type == MatchStrength.MISSING


def test_retrieve_candidates_ranks_and_limits_to_top_k():
    """Ranking here only needs to prefer matched over unmatched evidence
    and respect top_k — the full evidence-hierarchy hierarchy (experience
    outranking a bare skills mention) is Phase 6's job, layered on top of
    these raw signals, not Phase 5's."""
    pool = [
        _evidence("Optimized PostgreSQL queries reducing latency by 35%", ["PostgreSQL"], id="ev_001"),
        _evidence("PostgreSQL", ["PostgreSQL"], context=EvidenceContext.SKILLS, id="ev_002"),
        _evidence("Led a marketing campaign", [], id="ev_003"),
    ]
    results = _service.retrieve_candidates("req_1", "Experience with PostgreSQL", ["PostgreSQL"], pool, top_k=2)
    assert len(results) == 2
    result_ids = {r.evidence_id for r in results}
    assert "ev_003" not in result_ids  # the unrelated bullet must not outrank real matches
    assert all(r.signals.canonical == 1.0 for r in results)


def test_retrieve_candidates_empty_pool_returns_empty():
    assert _service.retrieve_candidates("req_1", "Python", ["Python"], []) == []


def test_determinism_repeated_calls_produce_identical_results():
    evidence = _evidence("Optimized PostgreSQL queries and reduced latency by 35%.", ["PostgreSQL"])
    results = [_service.match_evidence("req_1", "Experience with PostgreSQL", ["PostgreSQL"], evidence) for _ in range(3)]
    assert len({r.match_type for r in results}) == 1
    assert len({round(r.confidence, 6) for r in results}) == 1
    assert len({tuple(sorted(r.signals.model_dump().items())) for r in results}) == 1


def test_duplicate_evidence_does_not_multiply_signal():
    """Matching the same bullet twice must not produce a stronger result
    than matching it once — each call is independent and consistent."""
    evidence = _evidence("Built REST APIs using FastAPI and PostgreSQL")
    result_a = _service.match_evidence("req_1", "FastAPI", ["FastAPI"], evidence)
    result_b = _service.match_evidence("req_1", "FastAPI", ["FastAPI"], evidence)
    assert result_a.match_type == result_b.match_type
    assert result_a.confidence == result_b.confidence


def test_keyword_stuffing_does_not_increase_signal_unboundedly():
    stuffed = _evidence("Python Python Python Python Python Python Python Python", ["Python"] * 8)
    normal = _evidence("Built backend services using Python", ["Python"])
    stuffed_result = _service.match_evidence("req_1", "Python", ["Python"], stuffed)
    normal_result = _service.match_evidence("req_1", "Python", ["Python"], normal)
    # Both are legitimate exact/canonical matches; the stuffed version must
    # not exceed the normal, well-evidenced one.
    assert stuffed_result.signals.exact == normal_result.signals.exact == 1.0
    assert stuffed_result.confidence <= normal_result.confidence + 1e-9
