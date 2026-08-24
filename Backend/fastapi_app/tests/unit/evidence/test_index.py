from app.modules.evidence.index import build_evidence_pool
from app.modules.evidence.schemas import EvidenceSourceType
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf


def test_experience_bullet_carries_metrics_and_objects():
    text = (
        "Jane Doe\n\nEXPERIENCE\n"
        "Backend Intern, Example Co | Jun 2023 - Aug 2023\n"
        "- Reduced API latency by 35% using caching.\n"
    )
    resume = parse_pdf_bytes(build_pdf([text]))
    pool = build_evidence_pool(resume)
    bullet = next(item for item in pool if item.section == EvidenceSourceType.EXPERIENCE_BULLET)
    assert "35%" in bullet.metrics
    assert bullet.organization == "Example Co"


def test_ids_are_stable_and_unique():
    resume = parse_pdf_bytes(build_pdf(["Jane Doe\n\nSKILLS\nPython, FastAPI, Docker\n"]))
    pool_a = build_evidence_pool(resume)
    pool_b = build_evidence_pool(resume)
    assert [i.id for i in pool_a] == [i.id for i in pool_b]
    assert len(pool_a) == len(set(i.id for i in pool_a))
