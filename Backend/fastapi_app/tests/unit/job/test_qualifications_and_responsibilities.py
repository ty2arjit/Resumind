from app.modules.job.qualifications import build_qualifications
from app.modules.job.requirements import build_requirement
from app.modules.job.responsibilities import build_responsibilities
from app.modules.job.schemas import JDCanonicalSection


def test_qualification_view_extracts_degree_and_field():
    req = build_requirement(
        "Bachelor's degree in Computer Science or related field",
        JDCanonicalSection.QUALIFICATIONS_REQUIRED,
        "req_001",
    )
    qualifications = build_qualifications([req])
    assert len(qualifications) == 1
    assert qualifications[0].degree == "Bachelor's"
    assert "Computer Science" in qualifications[0].field


def test_responsibility_view_splits_action_and_object():
    req = build_requirement("Develop REST APIs using FastAPI.", JDCanonicalSection.RESPONSIBILITIES, "req_001")
    responsibilities = build_responsibilities([req])
    assert len(responsibilities) == 1
    assert responsibilities[0].action == "Develop"
    assert responsibilities[0].object == "REST APIs"


def test_non_matching_requirement_types_excluded_from_views():
    req = build_requirement("Strong experience with Python", JDCanonicalSection.QUALIFICATIONS_REQUIRED, "req_001")
    assert build_qualifications([req]) == []
    assert build_responsibilities([req]) == []
