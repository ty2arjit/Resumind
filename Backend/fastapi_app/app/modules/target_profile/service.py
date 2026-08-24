"""TargetProfileService — Target Fit analysis (spec Phase 9 §16-18, §21).
Reuses Phase 5's Matching Engine and Phase 6's Evidence Engine exactly as
Phase 7's ScoringService does; only the requirement source (a Target
Profile instead of a parsed JD) and the aggregation weights differ.
"""

from app.modules.evidence import EvidenceService
from app.modules.job.schemas import Requirement
from app.modules.normalization import NormalizationService
from app.modules.resume.schemas import StructuredResume
from app.modules.scoring.requirement_scoring import score_requirement
from app.modules.scoring.schemas import RequirementScoreResult, ScoringCategory
from app.modules.target_profile.config import ALGORITHM_VERSION, TargetProfileConfig, get_target_profile_config
from app.modules.target_profile.registry import TargetProfileRegistry
from app.modules.target_profile.requirements import build_target_requirements
from app.modules.target_profile.schemas import CustomRequirements, TargetAnalysisResult, TargetFitScores

#: spec §13-14 — Domain Fit is domain-knowledge evidence specifically;
#: every other requirement category (core skills, technologies,
#: responsibilities, experience, preferred skills) rolls into Position Fit.
_DOMAIN_FIT_CATEGORIES = {ScoringCategory.DOMAIN_KNOWLEDGE}


def _weighted_average(scores: list[RequirementScoreResult]) -> float | None:
    total_weight = sum(r.weight for r in scores)
    if total_weight <= 0:
        return None
    return sum(r.score * r.weight for r in scores) / total_weight


class TargetProfileService:
    def __init__(
        self,
        registry: TargetProfileRegistry | None = None,
        evidence_service: EvidenceService | None = None,
        config: TargetProfileConfig | None = None,
    ):
        self._registry = registry or TargetProfileRegistry()
        self._evidence = evidence_service or EvidenceService()
        self._config = config or get_target_profile_config()

    def analyze(
        self,
        raw_position: str,
        resume: StructuredResume,
        raw_domain: str | None = None,
        custom_requirements: CustomRequirements | None = None,
    ) -> TargetAnalysisResult:
        effective_profile = self._registry.build_effective_profile(raw_position, raw_domain, custom_requirements)
        target_requirements = build_target_requirements(
            effective_profile.effective, self._config.requirement_weights
        )

        requirement_scores = [self._score_target_requirement(req, resume) for req in target_requirements]

        position_scores = [r for r in requirement_scores if r.category not in _DOMAIN_FIT_CATEGORIES]
        domain_scores = [r for r in requirement_scores if r.category in _DOMAIN_FIT_CATEGORIES]

        position_fit = _weighted_average(position_scores)
        domain_fit = _weighted_average(domain_scores)

        weights = self._config.fit_dimension_weights
        available = [
            (position_fit, weights.position_fit),
            (domain_fit, weights.domain_fit),
        ]
        active_weight = sum(w for score, w in available if score is not None)
        target_fit_raw = (
            sum(score * w for score, w in available if score is not None) / active_weight
            if active_weight > 0
            else 0.0
        )

        matched = [r.text for r in requirement_scores if r.status in ("STRONG", "VERY_STRONG")]
        partial = [r.text for r in requirement_scores if r.status in ("PARTIAL", "WEAK")]
        missing = [r.text for r in requirement_scores if r.status == "MISSING"]

        return TargetAnalysisResult(
            target_profile=effective_profile.base_profile,
            scores=TargetFitScores(
                target_fit=round(max(0.0, min(1.0, target_fit_raw)) * 100),
                position_fit=round((position_fit or 0.0) * 100),
                domain_fit=round((domain_fit or 0.0) * 100),
            ),
            requirements=requirement_scores,
            matched_requirements=matched,
            partial_requirements=partial,
            missing_requirements=missing,
            algorithm_version=ALGORITHM_VERSION,
            profile_config_version=self._config.version,
            knowledge_version=effective_profile.base_profile.knowledge_version,
        )

    def _score_target_requirement(self, requirement: Requirement, resume: StructuredResume) -> RequirementScoreResult:
        evidence_result = self._evidence.retrieve_requirement_evidence(
            requirement.id,
            requirement.text,
            requirement.technologies,
            resume,
        )
        # Target requirements never carry AND-coverage semantics or
        # numeric experience/qualification evidence — an empty canonical
        # skill set is a safe no-op for score_requirement's AND-coverage
        # branch (it only runs when requirement.operator is set, which
        # build_target_requirements never sets).
        return score_requirement(requirement, evidence_result, set())
