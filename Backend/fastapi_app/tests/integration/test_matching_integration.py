"""Integration tests using real Phase 2/3/4 output (spec §31)."""

from app.models.enums import MatchStrength
from app.modules.matching import MatchingService, build_evidence_index
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf

_service = MatchingService()


def test_resume_postgres_matches_jd_postgresql_requirement():
    resume = parse_pdf_bytes(
        build_pdf(
            [
                "Jane Doe\njane@example.com\n\n"
                "EXPERIENCE\n"
                "Backend Intern, Example Co | Jun 2023 - Aug 2023\n"
                "- Optimized Postgres queries and reduced latency by 35%.\n"
            ]
        )
    )
    evidence_pool = build_evidence_index(resume)
    assert evidence_pool

    results = _service.retrieve_candidates("req_1", "Experience with PostgreSQL.", ["PostgreSQL"], evidence_pool)

    assert results
    top = results[0]
    assert top.explanation.canonical_entity_match is True
    assert top.explanation.canonical_value == "PostgreSQL"
    assert top.signals.semantic is not None
    assert top.match_type in (MatchStrength.STRONG, MatchStrength.VERY_STRONG, MatchStrength.PARTIAL)


def test_context_signal_differs_by_evidence_section():
    """The context signal (spec §15) must actually vary by section —
    Phase 6 is responsible for turning that into a full evidence
    hierarchy/ranking guarantee, but the raw signal has to be correct
    for it to build on."""
    resume = parse_pdf_bytes(
        build_pdf(
            [
                "Jane Doe\n\n"
                "EXPERIENCE\n"
                "Backend Intern, Example Co | Jun 2023 - Aug 2023\n"
                "- Optimized PostgreSQL queries and reduced latency by 35%.\n\n"
                "SKILLS\nPostgreSQL\n"
            ]
        )
    )
    evidence_pool = build_evidence_index(resume)
    results = _service.retrieve_candidates("req_1", "Experience with PostgreSQL.", ["PostgreSQL"], evidence_pool, top_k=10)

    by_section = {r.explanation.evidence_section: r.signals.context for r in results}
    assert by_section["EXPERIENCE"] > by_section["SKILLS"]
