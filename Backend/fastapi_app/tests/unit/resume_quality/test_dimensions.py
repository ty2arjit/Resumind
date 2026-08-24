"""Unit tests for individual Resume Quality dimensions, built directly
from StructuredResume objects (spec §33 cases 1-9, 11-13)."""

from app.modules.resume.schemas import (
    CanonicalSection,
    ContactInfo,
    DateRange,
    DetectedSection,
    DocumentMeta,
    DocumentFormat,
    EducationEntry,
    Evidence,
    ExperienceEntry,
    ExtractionStatus,
    ParsingWarning,
    ProjectEntry,
    SkillCategory,
    StructuredResume,
    WarningCode,
)
from app.modules.resume_quality import get_resume_quality_config
from app.modules.resume_quality.content_completeness import score_content_completeness
from app.modules.resume_quality.content_density import score_content_density
from app.modules.resume_quality.contact_completeness import score_contact_completeness
from app.modules.resume_quality.date_consistency import score_date_consistency
from app.modules.resume_quality.evidence_quality import score_evidence_quality
from app.modules.resume_quality.keyword_hygiene import score_keyword_hygiene
from app.modules.resume_quality.parseability import score_parseability
from app.modules.resume_quality.section_consistency import score_section_consistency
from app.modules.resume_quality.structure import score_structure

_CONFIG = get_resume_quality_config()


def _doc(status=ExtractionStatus.OK, text="some resume text " * 20, page_count=1):
    return DocumentMeta(format=DocumentFormat.PDF, page_count=page_count, raw_text=text, cleaned_text=text, extraction_status=status)


def _resume(**overrides) -> StructuredResume:
    base = dict(
        document=_doc(),
        sections=[],
        contact=ContactInfo(),
        experience=[],
        education=[],
        projects=[],
        skills=[],
        evidence=[],
        warnings=[],
    )
    base.update(overrides)
    return StructuredResume(**base)


# --- Case 1: highly structured resume -> strong parseability/structure ---

def test_highly_structured_resume_scores_well():
    resume = _resume(
        sections=[
            DetectedSection(canonical_type=CanonicalSection.EXPERIENCE, heading_text="Experience", confidence=0.9, start_line=0, end_line=5),
            DetectedSection(canonical_type=CanonicalSection.EDUCATION, heading_text="Education", confidence=0.9, start_line=6, end_line=8),
            DetectedSection(canonical_type=CanonicalSection.SKILLS, heading_text="Skills", confidence=0.9, start_line=9, end_line=10),
            DetectedSection(canonical_type=CanonicalSection.PROJECTS, heading_text="Projects", confidence=0.9, start_line=11, end_line=13),
        ],
        contact=ContactInfo(name="Jane Doe", email="jane@example.com"),
        experience=[
            ExperienceEntry(
                organization="Acme", role="Engineer",
                dates=DateRange(start_text="Jan 2021", end_text="Jan 2024", start_normalized="2021-01", end_normalized="2024-01"),
                bullets=["Built REST APIs."], raw_header="Engineer, Acme",
            )
        ],
        education=[EducationEntry(institution="XYZ University", degree="B.Tech", raw_text="B.Tech, XYZ")],
        skills=[SkillCategory(category="other", items=["Python", "FastAPI"])],
    )
    parseability, _ = score_parseability(resume, _CONFIG.parseability)
    structure, _ = score_structure(resume, _CONFIG.structure)
    assert parseability > 0.8
    assert structure > 0.8


# --- Case 2: sparse resume -> low completeness/density ---

def test_sparse_resume_scores_low_completeness_and_density():
    resume = _resume(contact=ContactInfo(name="Jane"))
    completeness, findings = score_content_completeness(resume, _CONFIG.content_completeness)
    density, density_findings = score_content_density(resume, _CONFIG.content_density)
    assert completeness < 0.5
    assert density < 0.5
    assert any(f.message_key == "NO_EXPERIENCE_OR_PROJECTS" for f in findings)
    assert any(f.message_key == "NO_BULLET_CONTENT" for f in density_findings)


# --- Case 3/4: strong vs weak evidence bullets ---

def test_strong_evidence_bullets_score_higher_than_weak():
    strong = _resume(
        evidence=[
            Evidence(text="Optimized PostgreSQL queries using indexing, reducing latency by 35%.",
                      section=CanonicalSection.EXPERIENCE, actions=["Optimized"], technologies=["PostgreSQL"],
                      metrics=["35%"], objects=["queries"])
        ]
    )
    weak = _resume(
        evidence=[Evidence(text="Worked on databases.", section=CanonicalSection.EXPERIENCE)]
    )
    strong_score, _ = score_evidence_quality(strong, _CONFIG.evidence_quality)
    weak_score, _ = score_evidence_quality(weak, _CONFIG.evidence_quality)
    assert strong_score > weak_score


# --- Case 5: malformed dates ---

def test_malformed_date_reduces_date_consistency():
    resume = _resume(
        experience=[
            ExperienceEntry(organization="Acme", role="Eng",
                             dates=DateRange(start_text="Sometime last year", start_normalized=None),
                             raw_header="Eng, Acme")
        ]
    )
    score, findings = score_date_consistency(resume, _CONFIG.date_consistency)
    assert score < 1.0
    assert any(f.message_key == "UNPARSEABLE_DATE" for f in findings)


def test_invalid_date_order_reduces_date_consistency():
    resume = _resume(
        experience=[
            ExperienceEntry(organization="Acme", role="Eng",
                             dates=DateRange(start_text="Jan 2024", end_text="Jan 2021", start_normalized="2024-01", end_normalized="2021-01"),
                             raw_header="Eng, Acme")
        ]
    )
    score, findings = score_date_consistency(resume, _CONFIG.date_consistency)
    assert score < 1.0
    assert any(f.message_key == "INVALID_DATE_ORDER" for f in findings)


# --- Case 6: missing dates entirely -> neutral default, not zero ---

def test_missing_dates_entirely_is_neutral_not_zero():
    resume = _resume(experience=[ExperienceEntry(organization="Acme", role="Eng", raw_header="Eng, Acme")])
    score, findings = score_date_consistency(resume, _CONFIG.date_consistency)
    assert score == _CONFIG.date_consistency.no_dates_default_score
    assert findings == []


# --- Case 7: duplicate content ---

def test_duplicate_evidence_reduces_keyword_hygiene():
    duplicated_text = "Built REST APIs using FastAPI."
    resume = _resume(
        evidence=[
            Evidence(text=duplicated_text, section=CanonicalSection.EXPERIENCE),
            Evidence(text=duplicated_text, section=CanonicalSection.PROJECTS),
            Evidence(text="Unrelated bullet about something else entirely.", section=CanonicalSection.EXPERIENCE),
        ]
    )
    score, findings = score_keyword_hygiene(resume, _CONFIG.keyword_hygiene)
    assert score < 1.0
    assert any(f.message_key == "EXCESSIVE_REPEATED_CONTENT" for f in findings)


# --- Case 8: excessive keyword repetition does not inflate quality ---

def test_repeated_identical_bullets_do_not_inflate_hygiene_score():
    text = "Python Python Python Python Python"
    resume = _resume(evidence=[Evidence(text=text, section=CanonicalSection.SKILLS) for _ in range(5)])
    score, findings = score_keyword_hygiene(resume, _CONFIG.keyword_hygiene)
    assert score < 0.7
    assert any(f.message_key == "EXCESSIVE_REPEATED_CONTENT" for f in findings)


# --- Case 9: good section structure ---

def test_consistent_experience_dates_score_high_section_consistency():
    resume = _resume(
        experience=[
            ExperienceEntry(organization="A", role="X", dates=DateRange(start_text="2020"), raw_header="X, A"),
            ExperienceEntry(organization="B", role="Y", dates=DateRange(start_text="2021"), raw_header="Y, B"),
        ]
    )
    score, findings = score_section_consistency(resume, _CONFIG.section_consistency)
    assert score == 1.0
    assert findings == []


def test_inconsistent_experience_dates_flagged():
    resume = _resume(
        experience=[
            ExperienceEntry(organization="A", role="X", dates=DateRange(start_text="2020"), raw_header="X, A"),
            ExperienceEntry(organization="B", role="Y", dates=None, raw_header="Y, B"),
        ]
    )
    score, findings = score_section_consistency(resume, _CONFIG.section_consistency)
    assert score == 0.5
    assert any(f.message_key == "INCONSISTENT_EXPERIENCE_DATES" for f in findings)


# --- Case 10: parsing warnings ---

def test_parsing_warnings_reduce_but_do_not_zero_parseability():
    resume = _resume(
        document=_doc(status=ExtractionStatus.LOW_TEXT),
        warnings=[
            ParsingWarning(code=WarningCode.LOW_EXTRACTED_TEXT, message="low text"),
            ParsingWarning(code=WarningCode.POSSIBLE_SCANNED_PDF, message="scanned"),
        ],
    )
    score, findings = score_parseability(resume, _CONFIG.parseability)
    assert 0.0 < score < 1.0
    assert len(findings) == 2


def test_single_warning_does_not_destroy_parseability():
    good_resume = _resume(
        sections=[DetectedSection(canonical_type=CanonicalSection.EXPERIENCE, heading_text="Experience", confidence=0.9, start_line=0, end_line=5)],
        contact=ContactInfo(name="Jane", email="jane@example.com"),
        warnings=[ParsingWarning(code=WarningCode.MALFORMED_DATE, message="one bad date")],
    )
    score, _ = score_parseability(good_resume, _CONFIG.parseability)
    assert score > 0.5


# --- Case 11: missing optional contact info ---

def test_missing_optional_contact_does_not_heavily_penalize():
    resume = _resume(contact=ContactInfo(name="Jane", email="jane@example.com"))
    score, findings = score_contact_completeness(resume, _CONFIG.contact_completeness)
    assert score >= _CONFIG.contact_completeness.core_weight
    assert findings == []


def test_missing_core_contact_is_flagged():
    resume = _resume(contact=ContactInfo(linkedin="linkedin.com/in/jane"))
    score, findings = score_contact_completeness(resume, _CONFIG.contact_completeness)
    assert score < 0.5
    assert any(f.message_key == "MISSING_CORE_CONTACT_INFO" for f in findings)


# --- Case 12/13: student vs experienced-professional resume structure ---

def test_student_style_resume_is_not_penalized_for_missing_experience():
    resume = _resume(
        education=[EducationEntry(institution="XYZ", degree="B.Tech", raw_text="B.Tech, XYZ")],
        projects=[ProjectEntry(name="Capstone", bullets=["Built a system."], raw_header="Capstone")],
        skills=[SkillCategory(category="other", items=["Python"])],
    )
    completeness, findings = score_content_completeness(resume, _CONFIG.content_completeness)
    assert completeness > 0.5
    assert not any(f.message_key == "NO_EXPERIENCE_OR_PROJECTS" for f in findings)


def test_experienced_professional_resume_scores_high_completeness():
    resume = _resume(
        experience=[ExperienceEntry(organization="Acme", role="Senior Eng", bullets=["Led a team."], raw_header="Senior Eng, Acme")],
        skills=[SkillCategory(category="other", items=["Python"])],
        achievements=["Employee of the year"],
    )
    completeness, _ = score_content_completeness(resume, _CONFIG.content_completeness)
    assert completeness >= 0.8
