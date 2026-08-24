"""Requirement-level deterministic scoring (spec Phase 7 §4-12, §21-23).

Consumes Phase 3 (Requirement), Phase 6 (RequirementEvidenceResult), and
Phase 4 (normalized resume skills) outputs — never re-runs parsing,
matching, or evidence retrieval itself.
"""

from app.models.enums import MatchStrength, RequirementType
from app.modules.evidence.schemas import ExperienceEvidence, QualificationEvidence, RequirementEvidenceResult
from app.modules.job.schemas import LogicalOperator, Requirement
from app.modules.normalization import NormalizationService
from app.modules.scoring.category_mapping import category_for_type
from app.modules.scoring.config import ScoringConfig, get_scoring_config
from app.modules.scoring.schemas import RequirementScoreResult

_normalization = NormalizationService()


def _score_experience(evidence: ExperienceEvidence, config: ScoringConfig) -> tuple[float, str]:
    thresholds = config.experience_scoring
    match_scores = config.match_strength_thresholds

    if evidence.required_years is None:
        return config.unknown_handling.neutral_score, "UNKNOWN"

    if evidence.detected_relevant_years is None:
        # Phase 5's experience matcher sets a high date_confidence only
        # when it confidently found *no* relevant entry at all (as
        # opposed to relevant entries with unreliable dates) — spec §10:
        # never silently turn "dates unreliable" into MISSING.
        if evidence.date_confidence >= 0.7:
            return match_scores.missing, "MISSING"
        return config.unknown_handling.neutral_score, "UNKNOWN"

    ratio = evidence.detected_relevant_years / evidence.required_years if evidence.required_years > 0 else 1.0
    if ratio >= thresholds.strong_ratio:
        return match_scores.very_strong, "VERY_STRONG"
    if ratio >= thresholds.partial_ratio:
        return match_scores.partial, "PARTIAL"
    if ratio >= thresholds.weak_ratio:
        return match_scores.weak, "WEAK"
    return match_scores.missing, "MISSING"


def _score_qualification(evidence: QualificationEvidence, config: ScoringConfig) -> tuple[float, str]:
    qconfig = config.qualification_scoring
    if evidence.matched and not evidence.uncertain:
        return qconfig.matched_confident_score, "VERY_STRONG"
    if evidence.matched and evidence.uncertain:
        return qconfig.matched_uncertain_score, "PARTIAL"
    # Not matched: distinguish "resume has education that just doesn't
    # satisfy this" (MISSING) from "no education evidence at all" (UNKNOWN).
    if evidence.degree or evidence.field:
        return qconfig.unmatched_score, "MISSING"
    return config.unknown_handling.neutral_score, "UNKNOWN"


#: How much of the score comes from the discrete MatchStrength->score
#: mapping (spec §12's literal example: "MISSING = 0.00") vs. the
#: continuous RequirementSignalWeights blend. The classification is the
#: anchor — it already incorporates Phase 5/6's hierarchy correction and
#: distinct-entity guardrails — the continuous blend only adds
#: within-bucket nuance. A pure continuous blend would let a MISSING
#: requirement (whose top "evidence" is really just the least-unrelated
#: candidate) show a confusing non-zero score alongside its MISSING label.
_ANCHOR_WEIGHT = 0.85
_REFINEMENT_WEIGHT = 0.15


def _score_from_matching_signals(evidence_result: RequirementEvidenceResult, config: ScoringConfig) -> tuple[float, str]:
    status = evidence_result.match_result.value
    anchor = getattr(config.match_strength_thresholds, evidence_result.match_result.value.lower(), 0.0)

    if not evidence_result.evidence:
        return anchor, status

    weights = config.requirement_signal_weights
    top = evidence_result.evidence[0]
    keyword = top.signals.lexical_relevance
    semantic = top.signals.semantic_similarity if top.signals.semantic_similarity is not None else 0.0
    context = top.signals.context_strength
    evidence_quality = evidence_result.aggregated_evidence_strength

    refinement = weights.keyword * keyword + weights.semantic * semantic + weights.evidence * evidence_quality + weights.context * context
    score = _ANCHOR_WEIGHT * anchor + _REFINEMENT_WEIGHT * refinement
    return max(0.0, min(1.0, score)), status


def _and_requirement_coverage(technologies: list[str], resume_canonical_skills: set[str]) -> float | None:
    """spec §23 — 'Python and FastAPI' requires both; Phase 5/6's
    canonical matching alone is satisfied by any one (the correct default
    for OR requirements), so AND requirements get an explicit coverage
    adjustment instead. Returns None when there's nothing to check
    (fewer than 2 resolvable technologies)."""
    canonicals = {
        result.canonical_value
        for result in (_normalization.normalize_skill(t) for t in technologies)
        if result.canonical_value is not None
    }
    if len(canonicals) < 2:
        return None
    covered = sum(1 for c in canonicals if c in resume_canonical_skills)
    return covered / len(canonicals)


def score_requirement(
    requirement: Requirement,
    evidence_result: RequirementEvidenceResult,
    resume_canonical_skills: set[str],
) -> RequirementScoreResult:
    config = get_scoring_config()
    category = category_for_type(requirement.type)

    if requirement.type == RequirementType.EXPERIENCE and evidence_result.experience is not None:
        score, status = _score_experience(evidence_result.experience, config)
    elif requirement.type == RequirementType.QUALIFICATION and evidence_result.qualification is not None:
        score, status = _score_qualification(evidence_result.qualification, config)
    elif evidence_result.match_result == MatchStrength.UNKNOWN:
        score, status = config.unknown_handling.neutral_score, "UNKNOWN"
    else:
        score, status = _score_from_matching_signals(evidence_result, config)

    if config.and_requirement.enabled and requirement.operator == LogicalOperator.AND:
        coverage = _and_requirement_coverage(requirement.technologies, resume_canonical_skills)
        if coverage is not None:
            score = score * coverage

    if requirement.critical and status == "MISSING":
        behavior = config.critical_requirement_behavior
        if behavior.apply_score_penalty:
            score = max(0.0, score - behavior.penalty_weight)

    top_evidence = evidence_result.evidence[0] if evidence_result.evidence else None

    return RequirementScoreResult(
        requirement_id=requirement.id,
        text=requirement.text,
        category=category,
        status=status,
        score=round(score, 6),
        importance=requirement.importance.value,
        weight=requirement.weight,
        critical=requirement.critical,
        evidence_text=top_evidence.text if top_evidence else None,
        evidence_source=_evidence_source_label(top_evidence) if top_evidence else None,
    )


_SOURCE_LABELS = {
    "EXPERIENCE_BULLET": "Experience",
    "PROJECT_BULLET": "Project",
    "SKILLS_SECTION": "Skills",
    "EDUCATION": "Education",
    "CERTIFICATION": "Certification",
    "SUMMARY": "Summary",
    "ACHIEVEMENT": "Achievement",
    "LEADERSHIP": "Leadership",
    "OTHER": "Resume",
}


def _evidence_source_label(evidence) -> str:
    label = _SOURCE_LABELS.get(evidence.section.value, "Resume")
    return f"{label} · {evidence.position}" if evidence.position else label
