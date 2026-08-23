from app.models.enums import ImportanceLevel, RequirementType
from app.modules.job.requirements import build_requirement, find_duplicate_groups, split_candidate_sentences
from app.modules.job.schemas import JDCanonicalSection


def _build(text, section=JDCanonicalSection.QUALIFICATIONS_REQUIRED, req_id="req_001"):
    return build_requirement(text, section, req_id)


# --- meaningfulness filtering (spec §5) ---

def test_generic_prose_is_not_a_requirement():
    assert _build("We are a fast-growing team building great products.") is None


def test_skill_mention_is_meaningful():
    req = _build("Strong experience with Python")
    assert req is not None
    assert req.type == RequirementType.SKILL


# --- type classification (spec §6) ---

def test_experience_years_classified_as_experience():
    req = _build("3+ years of backend development experience")
    assert req.type == RequirementType.EXPERIENCE
    assert req.experience is not None
    assert req.experience.min_years == 3.0


def test_degree_classified_as_qualification():
    req = _build("Bachelor's degree in Computer Science or related field")
    assert req.type == RequirementType.QUALIFICATION


def test_responsibility_bullet_in_responsibilities_section():
    req = _build("Design scalable backend services.", section=JDCanonicalSection.RESPONSIBILITIES)
    assert req.type == RequirementType.RESPONSIBILITY
    assert "Design" in req.actions


def test_tech_mention_classified_as_skill():
    req = _build("Knowledge of PostgreSQL")
    assert req.type == RequirementType.SKILL


def test_preferred_section_tech_classified_as_preferred_skill():
    req = _build("Experience with Redis", section=JDCanonicalSection.QUALIFICATIONS_PREFERRED)
    assert req.type == RequirementType.PREFERRED_SKILL


# --- importance (spec §7) ---

def test_must_have_is_required():
    req = _build("Must have Python experience.")
    assert req.importance == ImportanceLevel.REQUIRED


def test_preferred_wording_is_preferred():
    req = _build("Experience with Kubernetes is preferred.")
    assert req.importance == ImportanceLevel.PREFERRED


def test_a_plus_is_preferred():
    req = _build("Kafka experience is a plus.")
    assert req.importance == ImportanceLevel.PREFERRED


def test_section_context_drives_importance_when_wording_is_neutral():
    required = _build("Experience with Docker", section=JDCanonicalSection.QUALIFICATIONS_REQUIRED)
    preferred = _build("Experience with Docker", section=JDCanonicalSection.QUALIFICATIONS_PREFERRED)
    assert required.importance == ImportanceLevel.REQUIRED
    assert preferred.importance == ImportanceLevel.PREFERRED


def test_ambiguous_importance_is_unknown():
    req = _build("Knowledge of PostgreSQL", section=JDCanonicalSection.SKILLS)
    assert req.importance == ImportanceLevel.UNKNOWN


# --- critical (spec §8) ---

def test_mandatory_is_critical():
    req = _build("Python is mandatory.")
    assert req.importance == ImportanceLevel.REQUIRED
    assert req.critical is True


def test_required_prefix_is_critical():
    req = _build("Required: Bachelor's degree.")
    assert req.critical is True


def test_ordinary_required_wording_is_not_automatically_critical():
    req = _build("FastAPI experience is required.")
    assert req.importance == ImportanceLevel.REQUIRED
    assert req.critical is False


# --- weight (spec §9) — must come from centralized config, not be hardcoded ---

def test_weight_matches_centralized_scoring_config():
    from app.modules.scoring.config import get_scoring_config

    config = get_scoring_config()
    req = _build("Must have Python experience.")
    assert req.weight == config.requirement_importance_weights.required


# --- operators (spec §16) ---

def test_and_or_operators_detected():
    and_req = _build("Experience with Python and FastAPI")
    or_req = _build("Experience with AWS, Azure, or GCP")
    assert and_req.operator is not None and and_req.operator.value == "AND"
    assert or_req.operator is not None and or_req.operator.value == "OR"


# --- candidate sentence splitting ---

def test_bullets_become_individual_candidates():
    lines = ["- Strong Python skills", "- Experience with Docker"]
    candidates = split_candidate_sentences(lines)
    assert candidates == ["Strong Python skills", "Experience with Docker"]


def test_prose_paragraph_splits_into_sentences():
    lines = ["Must have Python experience. Experience with Docker is required."]
    candidates = split_candidate_sentences(lines)
    assert len(candidates) == 2


# --- duplicate detection (spec §19) ---

def test_detects_obvious_duplicates_after_normalization():
    req_a = _build("Experience with Python", req_id="req_001")
    req_b = _build("Strong Python experience", req_id="req_002")
    groups = find_duplicate_groups([req_a, req_b])
    assert len(groups) == 1
    assert len(groups[0]) == 2


def test_distinct_requirements_are_not_flagged_as_duplicates():
    req_a = _build("Experience with Python")
    req_b = _build("Experience with Java")
    assert find_duplicate_groups([req_a, req_b]) == []
