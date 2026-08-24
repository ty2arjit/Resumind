"""Centralized, versioned scoring configuration (spec §26-28, §59).

Every weight/threshold the scoring engine (Phase 7) will use must be read
from here — never hard-coded inline in a matching/scoring module. Phase 1
only establishes the structure; the numeric defaults below are the spec's
own illustrative examples (§23, §28), not tuned values. They exist so the
shape is real and testable, and must be recalibrated against the
evaluation benchmark (spec §52) before they mean anything in production.

`version` must be bumped whenever these numbers change, and every Analysis
row stores the version it was scored with (spec §44) so historical results
don't silently drift when the config is retuned later.
"""

from functools import lru_cache

from pydantic import BaseModel, field_validator

from app.models.enums import ImportanceLevel


class CategoryWeights(BaseModel):
    """Phase 7 §13/§15 — overall ATS score = sum(category_score *
    category_weight). Extends Phase 1's original six fields with
    domain_knowledge (spec §13's full category list), rebalanced so the
    total still sums to 1.0 — domain-knowledge requirements are rare in
    practice (Phase 3's classifier only assigns that type narrowly), so
    it gets the smallest non-zero share.
    """

    required_skills: float = 0.28
    responsibilities: float = 0.22
    experience: float = 0.18
    qualifications: float = 0.10
    preferred_skills: float = 0.10
    domain_knowledge: float = 0.07
    other: float = 0.05

    @field_validator("other")
    @classmethod
    def _weights_sum_to_one(cls, other: float, info) -> float:
        total = sum(info.data.values()) + other
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"category_weights must sum to 1.0, got {total}")
        return other


class RequirementSignalWeights(BaseModel):
    """Spec §26 — R_i = w_k*Keyword + w_s*Semantic + w_e*Evidence + w_c*Context."""

    keyword: float = 0.30
    semantic: float = 0.30
    evidence: float = 0.30
    context: float = 0.10

    @field_validator("context")
    @classmethod
    def _weights_sum_to_one(cls, context: float, info) -> float:
        total = sum(info.data.values()) + context
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"requirement signal weights must sum to 1.0, got {total}")
        return context


class SignalFusionWeights(BaseModel):
    """Phase 5 §21 — combines the raw per-technique signals (exact,
    canonical, keyword, tfidf, semantic, context) into ONE preliminary
    hybrid match strength per requirement-evidence pair. This is a
    distinct fusion step from RequirementSignalWeights above: that one
    combines {keyword, semantic, evidence, context} into a *final
    requirement score* once Phase 6/7 evidence-quality exists; this one
    runs earlier, before evidence quality is even computed.
    """

    exact: float = 0.25
    canonical: float = 0.25
    keyword: float = 0.15
    tfidf: float = 0.15
    semantic: float = 0.15
    context: float = 0.05

    @field_validator("context")
    @classmethod
    def _weights_sum_to_one(cls, context: float, info) -> float:
        total = sum(info.data.values()) + context
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"signal fusion weights must sum to 1.0, got {total}")
        return context


class MatchStrengthThresholds(BaseModel):
    """Spec §23 — initial normalized values for each MatchStrength bucket."""

    missing: float = 0.00
    weak: float = 0.30
    partial: float = 0.60
    strong: float = 0.85
    very_strong: float = 1.00


class EvidenceThresholds(BaseModel):
    """Minimum relevance score for a piece of evidence to be attached to a
    RequirementMatch at all, vs. surfaced as the top evidence for it."""

    minimum_relevance: float = 0.35
    top_evidence_relevance: float = 0.60


class EvidenceStrengthThresholds(BaseModel):
    """Phase 6 §16 — evidence strength is classified independently from
    match strength (spec uses MODERATE rather than PARTIAL here), even
    though the initial numeric buckets mirror MatchStrengthThresholds."""

    missing: float = 0.00
    weak: float = 0.30
    moderate: float = 0.60
    strong: float = 0.85
    very_strong: float = 1.00


class EvidenceAggregationConfig(BaseModel):
    """Phase 6 §8, §17-18 — how many evidence items to surface per
    requirement, and how much each additional item contributes beyond the
    strongest one (diminishing returns, spec §17: "three identical
    mentions should not produce 3x evidence strength")."""

    top_k_evidence: int = 3
    diminishing_weights: list[float] = [1.0, 0.35, 0.15, 0.08, 0.04]
    duplicate_text_similarity_threshold: float = 0.92


class CriticalRequirementBehavior(BaseModel):
    """Spec §29 — critical gaps are highlighted, not an automatic reject."""

    apply_score_penalty: bool = False
    penalty_weight: float = 0.0


class SemanticSimilarityThresholds(BaseModel):
    """Spec §22 — semantic similarity alone must not satisfy a requirement;
    these gate how much weight embedding similarity can carry."""

    minimum_considered: float = 0.40
    strong_match: float = 0.75


class RequirementImportanceWeights(BaseModel):
    """Initial per-requirement weight by importance (spec §9, §17) — used
    by the JD parser (Phase 3) as metadata only; it does not compute any
    score itself. These are the same illustrative values as
    CriticalRequirementBehavior's neighbors: unturned until the evaluation
    benchmark (spec §52) exists.
    """

    required: float = 1.0
    preferred: float = 0.6
    optional: float = 0.3
    unknown: float = 0.5

    def for_importance(self, importance: ImportanceLevel) -> float:
        return {
            ImportanceLevel.REQUIRED: self.required,
            ImportanceLevel.PREFERRED: self.preferred,
            ImportanceLevel.OPTIONAL: self.optional,
            ImportanceLevel.UNKNOWN: self.unknown,
        }[importance]


class EvidenceContextWeights(BaseModel):
    """Phase 5 §15 — provisional evidence-context strength by section.
    "Python" demonstrated in an EXPERIENCE bullet is stronger evidence
    than "Python" only appearing in a SKILLS list; this is that signal,
    not a final score.
    """

    experience: float = 0.95
    project: float = 0.85
    certification: float = 0.75
    education: float = 0.55
    skills: float = 0.55
    summary: float = 0.40
    other: float = 0.30

    def for_context(self, context: str) -> float:
        return getattr(self, context.lower(), self.other)


class UnknownHandlingConfig(BaseModel):
    """Phase 7 §10 — UNKNOWN must never be silently treated as MISSING.
    neutral_score is deliberately not 0.0: a requirement whose evidence
    couldn't be reliably evaluated (ambiguous entity, unreliable dates)
    should have limited impact on the score, not the same impact as a
    confirmed absence.
    """

    neutral_score: float = 0.5


class ExperienceScoringConfig(BaseModel):
    """Phase 7 §21 — maps a detected/required-years ratio to a match
    status. "2.5 of 3 years" should read as PARTIAL, not MISSING."""

    strong_ratio: float = 1.0
    partial_ratio: float = 0.66
    weak_ratio: float = 0.34


class QualificationScoringConfig(BaseModel):
    """Phase 7 §22."""

    matched_confident_score: float = 1.0
    matched_uncertain_score: float = 0.6
    unmatched_score: float = 0.0


class AndRequirementConfig(BaseModel):
    """Phase 7 §23 — "Python and FastAPI" requires both; Phase 5/6's
    canonical matching alone is satisfied by any one technology (correct
    default for OR requirements), so an explicit AND-coverage adjustment
    is applied here rather than duplicating a second matcher."""

    enabled: bool = True


class MatchingConfig(BaseModel):
    """Phase 5 — candidate-retrieval configuration. Kept separate from
    the signal-level configs above so "how many candidates to retrieve"
    can be tuned without touching scoring math.
    """

    top_k_candidates: int = 5


#: Code-version identifier for the scoring *algorithm* (spec §26) — bump
#: when the scoring logic itself changes shape, independent of config
#: value tuning (which bumps ScoringConfig.version instead).
ALGORITHM_VERSION = "ATS_ENGINE_V1"


class ScoringConfig(BaseModel):
    version: str = "SCORING_CONFIG_V1"
    category_weights: CategoryWeights = CategoryWeights()
    requirement_signal_weights: RequirementSignalWeights = RequirementSignalWeights()
    signal_fusion_weights: SignalFusionWeights = SignalFusionWeights()
    match_strength_thresholds: MatchStrengthThresholds = MatchStrengthThresholds()
    evidence_thresholds: EvidenceThresholds = EvidenceThresholds()
    critical_requirement_behavior: CriticalRequirementBehavior = CriticalRequirementBehavior()
    semantic_similarity_thresholds: SemanticSimilarityThresholds = SemanticSimilarityThresholds()
    requirement_importance_weights: RequirementImportanceWeights = RequirementImportanceWeights()
    matching: MatchingConfig = MatchingConfig()
    evidence_context_weights: EvidenceContextWeights = EvidenceContextWeights()
    evidence_strength_thresholds: EvidenceStrengthThresholds = EvidenceStrengthThresholds()
    evidence_aggregation: EvidenceAggregationConfig = EvidenceAggregationConfig()
    unknown_handling: UnknownHandlingConfig = UnknownHandlingConfig()
    experience_scoring: ExperienceScoringConfig = ExperienceScoringConfig()
    qualification_scoring: QualificationScoringConfig = QualificationScoringConfig()
    and_requirement: AndRequirementConfig = AndRequirementConfig()


@lru_cache
def get_scoring_config() -> ScoringConfig:
    """Returns the active scoring configuration.

    A single cached instance for now (config is code-defined). Loading this
    from a versioned file/table instead is a reasonable Phase 7 extension —
    call sites should already depend on get_scoring_config() rather than
    constructing ScoringConfig() themselves, so that change stays isolated
    here.
    """
    return ScoringConfig()
