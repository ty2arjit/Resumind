from app.models.enums import ImportanceLevel, RequirementType
from app.modules.job.schemas import Requirement
from app.modules.scoring.category_scoring import mark_duplicates, score_categories
from app.modules.scoring.schemas import RequirementScoreResult, ScoringCategory


def _score(id, category, score, weight=1.0):
    return RequirementScoreResult(
        requirement_id=id, text=id, category=category, status="STRONG", score=score,
        importance="REQUIRED", weight=weight,
    )


def test_category_score_is_weighted_average():
    scores = [_score("req_1", ScoringCategory.REQUIRED_SKILLS, 1.0, weight=1.0), _score("req_2", ScoringCategory.REQUIRED_SKILLS, 0.0, weight=1.0)]
    result = score_categories(scores)
    assert result[ScoringCategory.REQUIRED_SKILLS].score == 0.5


def test_higher_weight_requirement_dominates_category_score():
    scores = [_score("req_1", ScoringCategory.REQUIRED_SKILLS, 1.0, weight=3.0), _score("req_2", ScoringCategory.REQUIRED_SKILLS, 0.0, weight=1.0)]
    result = score_categories(scores)
    assert result[ScoringCategory.REQUIRED_SKILLS].score == 0.75


def test_absent_category_does_not_appear():
    scores = [_score("req_1", ScoringCategory.REQUIRED_SKILLS, 0.8)]
    result = score_categories(scores)
    assert ScoringCategory.QUALIFICATIONS not in result


def test_duplicate_requirements_excluded_from_category_aggregation():
    requirements = [
        Requirement(id="req_1", text="Experience with Python", type=RequirementType.SKILL, importance=ImportanceLevel.REQUIRED, weight=1.0, confidence=0.9, technologies=["Python"]),
        Requirement(id="req_2", text="Strong Python experience", type=RequirementType.SKILL, importance=ImportanceLevel.REQUIRED, weight=1.0, confidence=0.9, technologies=["Python"]),
    ]
    scores = [
        _score("req_1", ScoringCategory.REQUIRED_SKILLS, 1.0),
        _score("req_2", ScoringCategory.REQUIRED_SKILLS, 0.0),  # would drag the average down if counted
    ]
    mark_duplicates(requirements, scores)
    assert scores[1].duplicate_of == "req_1"

    result = score_categories(scores)
    assert result[ScoringCategory.REQUIRED_SKILLS].score == 1.0
    assert result[ScoringCategory.REQUIRED_SKILLS].requirement_count == 1


def test_non_duplicate_requirements_are_unaffected():
    requirements = [
        Requirement(id="req_1", text="Python", type=RequirementType.SKILL, importance=ImportanceLevel.REQUIRED, weight=1.0, confidence=0.9, technologies=["Python"]),
        Requirement(id="req_2", text="Java", type=RequirementType.SKILL, importance=ImportanceLevel.REQUIRED, weight=1.0, confidence=0.9, technologies=["Java"]),
    ]
    scores = [_score("req_1", ScoringCategory.REQUIRED_SKILLS, 1.0), _score("req_2", ScoringCategory.REQUIRED_SKILLS, 0.5)]
    mark_duplicates(requirements, scores)
    assert all(s.duplicate_of is None for s in scores)
