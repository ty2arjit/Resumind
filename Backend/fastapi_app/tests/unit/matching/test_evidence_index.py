from app.modules.matching.evidence_index import build_evidence_index
from app.modules.matching.schemas import EvidenceContext
from app.modules.resume.parser import parse_pdf_bytes
from tests.fixtures.builders import build_pdf


def test_builds_evidence_from_all_resume_sections():
    text = (
        "Jane Doe\njane@example.com\n\n"
        "SUMMARY\nExperienced backend engineer.\n\n"
        "EXPERIENCE\nBackend Intern, Example Co | Jun 2023 - Aug 2023\n"
        "- Built REST APIs using FastAPI.\n\n"
        "SKILLS\nPython, FastAPI\n\n"
        "CERTIFICATIONS\nAWS Certified Solutions Architect\n"
    )
    resume = parse_pdf_bytes(build_pdf([text]))
    index = build_evidence_index(resume)

    contexts = {item.context for item in index}
    assert EvidenceContext.EXPERIENCE in contexts
    assert EvidenceContext.SKILLS in contexts
    assert EvidenceContext.CERTIFICATION in contexts
    assert EvidenceContext.SUMMARY in contexts


def test_evidence_ids_are_unique_and_stable():
    text = "Jane Doe\n\nSKILLS\nPython, FastAPI, Docker\n"
    resume = parse_pdf_bytes(build_pdf([text]))
    index_a = build_evidence_index(resume)
    index_b = build_evidence_index(resume)
    assert [e.id for e in index_a] == [e.id for e in index_b]
    assert len(index_a) == len(set(e.id for e in index_a))


def test_empty_resume_produces_empty_index():
    resume = parse_pdf_bytes(build_pdf(["Jane Doe\n"]))
    assert build_evidence_index(resume) == []
