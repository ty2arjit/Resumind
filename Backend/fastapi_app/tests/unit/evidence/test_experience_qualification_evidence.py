from app.modules.evidence.experience_evidence import build_experience_evidence
from app.modules.evidence.qualification_evidence import build_qualification_evidence
from app.modules.resume.schemas import DateRange, EducationEntry, ExperienceEntry


def test_experience_evidence_reports_relevant_duration():
    entry = ExperienceEntry(
        organization="Example Co", role="Backend Engineer", dates=DateRange(duration_months=36),
        technologies=["Python"], raw_header="x",
    )
    result = build_experience_evidence(3.0, ["Python"], "Python development", [entry])
    assert result.detected_relevant_years == 3.0
    assert "Example Co" in result.supporting_experience[0]


def test_no_requirement_returns_none():
    assert build_experience_evidence(None, [], None, []) is None


def test_qualification_evidence_reports_institution():
    entry = EducationEntry(institution="NIT Rourkela", degree="B.Tech", field="Computer Science", raw_text="x")
    result = build_qualification_evidence("Bachelor's", "Computer Science", [entry])
    assert result.institution == "NIT Rourkela"
    assert result.matched is True


def test_no_qualification_requirement_returns_none():
    assert build_qualification_evidence(None, None, []) is None
