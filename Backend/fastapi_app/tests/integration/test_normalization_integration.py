"""Integration tests using real Phase 2 (resume) and Phase 3 (JD) parser
output (spec §24) — the exact scenario Phase 5's matching engine will
depend on: a resume's raw mention and a JD's raw mention of the same
underlying technology must resolve to the same canonical value.
"""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.normalization import NormalizationService
from app.modules.resume.parser import parse_pdf_bytes as parse_resume_pdf
from tests.fixtures.builders import build_pdf


def test_resume_postgres_and_jd_postgresql_resolve_to_same_canonical():
    resume = parse_resume_pdf(
        build_pdf(["Jane Doe\njane@example.com\n\nSKILLS\nPostgres, Python3, ReactJS\n"])
    )
    jd = parse_jd_text("Backend Engineer\n\nSKILLS\nPostgreSQL, Python, React\n")

    svc = NormalizationService()
    normalized_resume = svc.normalize_resume(resume)
    normalized_jd = svc.normalize_job_description(jd)

    resume_canonicals = {e.canonical_value for e in normalized_resume.skills}
    jd_canonicals = {e.canonical_value for e in normalized_jd.skills}

    assert resume_canonicals == {"PostgreSQL", "Python", "React"}
    assert jd_canonicals == {"PostgreSQL", "Python", "React"}
    assert resume_canonicals == jd_canonicals


def test_normalize_resume_deduplicates_across_sections():
    """A resume mentioning the same technology in both its SKILLS list
    and a project bullet must still produce one entity per unique raw
    mention, not one per occurrence."""
    text = (
        "Jane Doe\njane@example.com\n\n"
        "SKILLS\nPython, FastAPI\n\n"
        "PROJECTS\nResumind | Python, FastAPI\n- Built things using Python.\n"
    )
    resume = parse_resume_pdf(build_pdf([text]))
    svc = NormalizationService()
    normalized = svc.normalize_resume(resume)

    python_mentions = [e for e in normalized.skills if e.raw_value == "Python"]
    assert len(python_mentions) == 1


def test_normalize_job_description_covers_requirement_technologies():
    jd = parse_jd_text("Backend Engineer\n\nREQUIREMENTS\n- Strong experience with Docker and Kubernetes.\n")
    svc = NormalizationService()
    normalized = svc.normalize_job_description(jd)
    canonicals = {e.canonical_value for e in normalized.skills}
    assert {"Docker", "Kubernetes"}.issubset(canonicals)


def test_knowledge_version_flows_through_batch_results():
    resume = parse_resume_pdf(build_pdf(["Jane Doe\n\nSKILLS\nPython\n"]))
    svc = NormalizationService()
    normalized = svc.normalize_resume(resume)
    assert normalized.knowledge_version == "KNOWLEDGE_V1"
    assert all(e.knowledge_version == "KNOWLEDGE_V1" for e in normalized.skills)
