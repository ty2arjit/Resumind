"""Adversarial tests (spec Phase 13 §11-12, §30) — resumes deliberately
constructed to try to game the ATS. The scorer must resist obvious
gaming strategies without any special-cased "anti-cheat" logic; these
tests only verify the emergent behavior of the real pipeline."""

from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume.parser import parse_pdf_bytes
from app.modules.scoring import ScoringService
from tests.fixtures.builders import build_pdf

_service = ScoringService()
_JD = "Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n"


def _score(resume_text):
    resume = parse_pdf_bytes(build_pdf([resume_text]))
    jd = parse_jd_text(_JD)
    return _service.calculate_ats_alignment(jd, resume).ats_alignment


# --- Keyword stuffing (§11, §30.1) ---

def test_keyword_stuffing_does_not_beat_genuine_evidence():
    resume_a_strong_evidence_once = (
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python, serving 50K daily users.\n\nSKILLS\nPython, FastAPI\n"
    )
    resume_b_stuffed = "Jane Doe\njane@example.com\n\nSKILLS\n" + ", ".join(["Python"] * 20) + "\n"

    score_a = _score(resume_a_strong_evidence_once)
    score_b = _score(resume_b_stuffed)
    # Repeating the same keyword 20x must not provide a meaningfully
    # larger score than a single genuine mention backed by real
    # experience evidence — a few points of noise either way is fine,
    # but stuffing must not "dramatically" win (spec §11).
    assert score_b - score_a <= 5


# --- Duplicate content (§12) ---

def test_duplicated_experience_entry_does_not_inflate_score_beyond_single_copy():
    single = (
        "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python, serving 50K daily users.\n\nSKILLS\nPython\n"
    )
    duplicated = (
        "Jane Doe\njane@example.com\n\n"
        "EXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
        "- Built REST APIs using Python, serving 50K daily users.\n\n"
        "PROJECTS\nAPI Platform\n- Built REST APIs using Python, serving 50K daily users.\n\n"
        "SKILLS\nPython\n"
    )
    score_single = _score(single)
    score_duplicated = _score(duplicated)
    # Some increase from a second, independent-looking mention is
    # plausible (diminishing-returns aggregation still counts it a
    # little — spec Phase 6 §17), but it must not multiply the score.
    assert score_duplicated <= score_single * 1.5


# --- Copying JD keywords without evidence (§30.7) ---

def test_copying_jd_language_verbatim_without_evidence_is_not_strong():
    resume = "Jane Doe\njane@example.com\n\nSUMMARY\nExperience with Python.\n\nSKILLS\nCommunication\n"
    resume_parsed = parse_pdf_bytes(build_pdf([resume]))
    jd = parse_jd_text(_JD)
    breakdown = _service.calculate_ats_alignment(jd, resume_parsed)
    requirement = breakdown.requirements[0]
    assert requirement.status not in ("VERY_STRONG",)


# --- Massive skills section (§30.3) ---

def test_massive_unrelated_skills_section_does_not_satisfy_the_requirement():
    unrelated_skills = ", ".join(
        ["Photoshop", "Illustrator", "Excel", "PowerPoint", "Word", "Salesforce", "SAP", "Tableau", "Figma", "Sketch"]
    )
    resume = f"Jane Doe\njane@example.com\n\nSKILLS\n{unrelated_skills}\n"
    resume_parsed = parse_pdf_bytes(build_pdf([resume]))
    jd = parse_jd_text(_JD)
    breakdown = _service.calculate_ats_alignment(jd, resume_parsed)
    requirement = breakdown.requirements[0]
    assert requirement.status in ("MISSING", "UNKNOWN")
