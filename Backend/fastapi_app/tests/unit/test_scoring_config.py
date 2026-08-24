from app.modules.scoring.config import ScoringConfig, get_scoring_config


def test_category_weights_sum_to_one():
    config = ScoringConfig()
    weights = config.category_weights
    total = (
        weights.required_skills
        + weights.responsibilities
        + weights.experience
        + weights.qualifications
        + weights.preferred_skills
        + weights.domain_knowledge
        + weights.other
    )
    assert abs(total - 1.0) < 1e-6


def test_requirement_signal_weights_sum_to_one():
    config = ScoringConfig()
    weights = config.requirement_signal_weights
    total = weights.keyword + weights.semantic + weights.evidence + weights.context
    assert abs(total - 1.0) < 1e-6


def test_invalid_category_weights_are_rejected():
    import pytest

    with pytest.raises(ValueError):
        ScoringConfig(category_weights={"required_skills": 0.9, "other": 0.9})


def test_get_scoring_config_is_versioned_and_cached():
    config_a = get_scoring_config()
    config_b = get_scoring_config()
    assert config_a is config_b
    assert config_a.version
