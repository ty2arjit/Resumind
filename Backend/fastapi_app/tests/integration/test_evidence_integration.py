"""Integration test using real Phase 2-5 output (spec §29)."""

from app.modules.evidence import EvidenceService
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf

_service = EvidenceService()


def test_experience_bullet_outranks_skills_mention_end_to_end():
    resume = parse_pdf_bytes(
        build_pdf(
            [
                "Jane Doe\n\nSKILLS\nPostgres\n\n"
                "EXPERIENCE\nBackend Intern, Co | Jun 2023 - Aug 2023\n"
                "- Optimized PostgreSQL queries and reduced latency by 35%.\n"
            ]
        )
    )
    result = _service.retrieve_requirement_evidence("req_1", "Experience with PostgreSQL.", ["PostgreSQL"], resume, top_k=5)

    assert result.evidence
    top = result.evidence[0]
    assert top.section.value == "EXPERIENCE_BULLET"
    assert top.signals.canonical_entity_match == 1.0
