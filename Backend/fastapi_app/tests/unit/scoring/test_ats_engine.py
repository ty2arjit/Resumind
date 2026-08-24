from app.modules.scoring.ats_engine import calculate_ats_score, calculate_contributions, normalize_active_category_weights
from app.modules.scoring.schemas import CategoryScoreResult, RequirementScoreResult, ScoringCategory


def _category(category, score, configured_weight):
    return CategoryScoreResult(category=category, score=score, configured_weight=configured_weight, normalized_weight=0.0, requirement_count=1)


def test_active_category_weights_renormalize_to_one():
    """spec §15: a JD missing a category (e.g. no Qualifications) must
    not silently score it 0 — the remaining active weights renormalize."""
    categories = {
        ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 0.8, 0.28),
        ScoringCategory.RESPONSIBILITIES: _category(ScoringCategory.RESPONSIBILITIES, 0.6, 0.22),
    }
    normalized = normalize_active_category_weights(categories)
    total = sum(r.normalized_weight for r in normalized.values())
    assert abs(total - 1.0) < 1e-9


def test_full_category_set_normalization_is_a_no_op_ratio():
    from app.modules.scoring.config import get_scoring_config

    weights = get_scoring_config().category_weights
    categories = {
        ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 1.0, weights.required_skills),
        ScoringCategory.RESPONSIBILITIES: _category(ScoringCategory.RESPONSIBILITIES, 1.0, weights.responsibilities),
        ScoringCategory.EXPERIENCE: _category(ScoringCategory.EXPERIENCE, 1.0, weights.experience),
        ScoringCategory.QUALIFICATIONS: _category(ScoringCategory.QUALIFICATIONS, 1.0, weights.qualifications),
        ScoringCategory.PREFERRED_SKILLS: _category(ScoringCategory.PREFERRED_SKILLS, 1.0, weights.preferred_skills),
        ScoringCategory.DOMAIN_KNOWLEDGE: _category(ScoringCategory.DOMAIN_KNOWLEDGE, 1.0, weights.domain_knowledge),
        ScoringCategory.OTHER: _category(ScoringCategory.OTHER, 1.0, weights.other),
    }
    normalized = normalize_active_category_weights(categories)
    for category, result in normalized.items():
        assert abs(result.normalized_weight - getattr(weights, category.value.lower())) < 1e-9


def test_score_is_bounded_0_to_100():
    categories = normalize_active_category_weights({ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 1.0, 1.0)})
    assert calculate_ats_score(categories) == 100

    categories_zero = normalize_active_category_weights({ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 0.0, 1.0)})
    assert calculate_ats_score(categories_zero) == 0


def test_empty_categories_scores_zero():
    assert calculate_ats_score({}) == 0


def test_contributions_sum_to_approximately_the_final_score():
    categories = normalize_active_category_weights(
        {
            ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 0.8, 0.5),
            ScoringCategory.EXPERIENCE: _category(ScoringCategory.EXPERIENCE, 0.6, 0.5),
        }
    )
    requirements = [
        RequirementScoreResult(requirement_id="req_1", text="x", category=ScoringCategory.REQUIRED_SKILLS, status="STRONG", score=0.8, importance="REQUIRED", weight=1.0),
        RequirementScoreResult(requirement_id="req_2", text="y", category=ScoringCategory.EXPERIENCE, status="STRONG", score=0.6, importance="REQUIRED", weight=1.0),
    ]
    calculate_contributions(requirements, categories)
    ats_score = calculate_ats_score(categories)
    assert abs(sum(r.contribution for r in requirements) - ats_score) < 0.5


def test_duplicate_requirement_has_zero_contribution():
    categories = normalize_active_category_weights({ScoringCategory.REQUIRED_SKILLS: _category(ScoringCategory.REQUIRED_SKILLS, 1.0, 1.0)})
    requirements = [
        RequirementScoreResult(requirement_id="req_1", text="x", category=ScoringCategory.REQUIRED_SKILLS, status="STRONG", score=1.0, importance="REQUIRED", weight=1.0),
        RequirementScoreResult(requirement_id="req_2", text="x2", category=ScoringCategory.REQUIRED_SKILLS, status="STRONG", score=1.0, importance="REQUIRED", weight=1.0, duplicate_of="req_1"),
    ]
    calculate_contributions(requirements, categories)
    assert requirements[1].contribution == 0.0
