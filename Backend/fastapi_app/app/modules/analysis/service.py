"""AnalysisService — the interpretation layer (spec Phase 10 §1, §25-26).
Consumes Phase 5-9 outputs and never reimplements their scoring/matching
logic; it only detects strengths/gaps and generates recommendations from
already-computed structured results.
"""

from app.models.enums import AnalysisMode
from app.modules.analysis.config import ALGORITHM_VERSION, AnalysisConfig, get_analysis_config
from app.modules.analysis.gaps import detect_requirement_gaps, detect_resume_quality_gaps
from app.modules.analysis.recommendations import generate_recommendations_from_gaps, prioritize_recommendations
from app.modules.analysis.schemas import (
    AlgorithmVersions,
    Analysis,
    AnalysisContext,
    AnalysisScores,
    AnalysisSource,
    AnalysisSummary,
    Gap,
    Recommendation,
    Strength,
)
from app.modules.analysis.strengths import detect_fit_strengths, detect_quality_strengths, detect_requirement_strengths, prioritize_strengths
from app.modules.job.schemas import StructuredJD
from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality import ResumeQualityService
from app.modules.resume_quality.config import ALGORITHM_VERSION as RESUME_QUALITY_ALGORITHM_VERSION
from app.modules.scoring import ScoringService
from app.modules.scoring.config import ALGORITHM_VERSION as ATS_ALGORITHM_VERSION
from app.modules.target_profile import CustomRequirements, TargetProfileService
from app.modules.target_profile.config import get_target_profile_config


class AnalysisService:
    def __init__(
        self,
        scoring_service: ScoringService | None = None,
        resume_quality_service: ResumeQualityService | None = None,
        target_profile_service: TargetProfileService | None = None,
        config: AnalysisConfig | None = None,
    ):
        self._scoring = scoring_service or ScoringService()
        self._resume_quality = resume_quality_service or ResumeQualityService()
        self._target_profile = target_profile_service or TargetProfileService()
        self._config = config or get_analysis_config()

    def run_jd_analysis(self, jd: StructuredJD, resume: StructuredResume) -> Analysis:
        breakdown = self._scoring.calculate_ats_alignment(jd, resume)
        quality = self._resume_quality.analyze(resume)

        category_weights = {category: result.normalized_weight for category, result in breakdown.categories.items()}
        gaps = detect_requirement_gaps(breakdown.requirements, category_weights, self._config, AnalysisSource.JD)
        gaps += detect_resume_quality_gaps(quality.findings, self._config)

        strengths = detect_requirement_strengths(breakdown.requirements, self._config, AnalysisSource.JD)
        strengths += detect_quality_strengths(quality.dimension_scores, self._config)

        recommendations = generate_recommendations_from_gaps(gaps)

        scores = AnalysisScores(ats_alignment=breakdown.ats_alignment, resume_quality=quality.resume_quality)
        versions = AlgorithmVersions(
            analysis=ALGORITHM_VERSION,
            ats=ATS_ALGORITHM_VERSION,
            resume_quality=RESUME_QUALITY_ALGORITHM_VERSION,
            matching=breakdown.algorithm_version,
            knowledge=breakdown.knowledge_version,
        )

        strongest, weakest = _strongest_weakest_category(breakdown.categories)

        return self._build_analysis(
            context=AnalysisContext(mode=AnalysisMode.JD),
            scores=scores,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
            versions=versions,
            primary_score=breakdown.ats_alignment,
            score_type="ATS_ALIGNMENT",
            strongest_area=strongest,
            weakest_area=weakest,
            categories={category: result.model_dump() for category, result in breakdown.categories.items()},
            requirements=breakdown.requirements,
        )

    def run_target_analysis(
        self,
        position: str,
        resume: StructuredResume,
        domain: str | None = None,
        custom_requirements: CustomRequirements | None = None,
    ) -> Analysis:
        target_result = self._target_profile.analyze(position, resume, domain, custom_requirements)
        quality = self._resume_quality.analyze(resume)

        fit_weights = get_target_profile_config().fit_dimension_weights  # Phase 9's own config, not recomputed
        category_weights = {
            "DOMAIN_KNOWLEDGE": fit_weights.domain_fit,
        }
        default_weight = fit_weights.position_fit
        category_weights_full = {
            category.value: category_weights.get(category.value, default_weight)
            for category in {r.category for r in target_result.requirements}
        }

        gaps = detect_requirement_gaps(
            target_result.requirements, category_weights_full, self._config, AnalysisSource.TARGET_PROFILE
        )
        gaps += detect_resume_quality_gaps(quality.findings, self._config)

        strengths = detect_requirement_strengths(target_result.requirements, self._config, AnalysisSource.TARGET_PROFILE)
        strengths += detect_fit_strengths(target_result.scores.position_fit, target_result.scores.domain_fit, self._config)
        strengths += detect_quality_strengths(quality.dimension_scores, self._config)

        recommendations = generate_recommendations_from_gaps(gaps)

        scores = AnalysisScores(
            target_fit=target_result.scores.target_fit,
            position_fit=target_result.scores.position_fit,
            domain_fit=target_result.scores.domain_fit,
            resume_quality=quality.resume_quality,
        )
        versions = AlgorithmVersions(
            analysis=ALGORITHM_VERSION,
            resume_quality=RESUME_QUALITY_ALGORITHM_VERSION,
            target_fit=target_result.algorithm_version,
            knowledge=target_result.knowledge_version,
        )

        strongest = "Position Fit" if target_result.scores.position_fit >= target_result.scores.domain_fit else "Domain Fit"
        weakest = "Domain Fit" if strongest == "Position Fit" else "Position Fit"

        return self._build_analysis(
            context=AnalysisContext(
                mode=AnalysisMode.TARGET_PROFILE,
                target_profile_position=target_result.target_profile.position.canonical,
                target_profile_domain=target_result.target_profile.domain.canonical,
            ),
            scores=scores,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
            versions=versions,
            primary_score=target_result.scores.target_fit,
            score_type="TARGET_FIT",
            strongest_area=strongest,
            weakest_area=weakest,
            requirements=target_result.requirements,
        )

    def run_combined_analysis(
        self,
        jd: StructuredJD,
        resume: StructuredResume,
        position: str,
        domain: str | None = None,
        custom_requirements: CustomRequirements | None = None,
    ) -> Analysis:
        """spec §21 — Specific JD is authoritative; Target Profile is
        contextual. Ordering: JD gaps, JD strengths, Target Profile gaps,
        Resume Quality issues."""
        jd_analysis = self.run_jd_analysis(jd, resume)
        target_analysis = self.run_target_analysis(position, resume, domain, custom_requirements)

        jd_gaps = [g for g in jd_analysis.gaps if g.source == AnalysisSource.JD]
        quality_gaps = [g for g in jd_analysis.gaps if g.source == AnalysisSource.RESUME_QUALITY]
        target_gaps = [g for g in target_analysis.gaps if g.source == AnalysisSource.TARGET_PROFILE]

        combined_gaps = jd_gaps + target_gaps + quality_gaps
        combined_strengths = jd_analysis.strengths + [
            s for s in target_analysis.strengths if s.source != AnalysisSource.RESUME_QUALITY
        ]
        combined_recommendations = generate_recommendations_from_gaps(combined_gaps)

        scores = AnalysisScores(
            ats_alignment=jd_analysis.scores.ats_alignment,
            resume_quality=jd_analysis.scores.resume_quality,
            target_fit=target_analysis.scores.target_fit,
            position_fit=target_analysis.scores.position_fit,
            domain_fit=target_analysis.scores.domain_fit,
        )
        versions = AlgorithmVersions(
            analysis=ALGORITHM_VERSION,
            ats=jd_analysis.algorithm_versions.ats,
            resume_quality=jd_analysis.algorithm_versions.resume_quality,
            target_fit=target_analysis.algorithm_versions.target_fit,
            matching=jd_analysis.algorithm_versions.matching,
            knowledge=jd_analysis.algorithm_versions.knowledge,
        )

        return self._build_analysis(
            context=AnalysisContext(
                mode=AnalysisMode.COMBINED,
                target_profile_position=target_analysis.context.target_profile_position,
                target_profile_domain=target_analysis.context.target_profile_domain,
            ),
            scores=scores,
            strengths=combined_strengths,
            gaps=combined_gaps,
            recommendations=combined_recommendations,
            versions=versions,
            primary_score=jd_analysis.scores.ats_alignment or 0,
            score_type="ATS_ALIGNMENT",
            strongest_area=jd_analysis.summary.strongest_area,
            weakest_area=jd_analysis.summary.weakest_area,
            categories=jd_analysis.categories,
            requirements=jd_analysis.requirements + target_analysis.requirements,
        )

    def _build_analysis(
        self,
        context: AnalysisContext,
        scores: AnalysisScores,
        strengths: list[Strength],
        gaps: list[Gap],
        recommendations: list[Recommendation],
        versions: AlgorithmVersions,
        primary_score: int,
        score_type: str,
        strongest_area: str | None,
        weakest_area: str | None,
        categories: dict[str, dict] | None = None,
        requirements: list | None = None,
    ) -> Analysis:
        top_strengths = prioritize_strengths(strengths, self._config)
        top_recommendations = prioritize_recommendations(recommendations, self._config)

        critical_count = sum(1 for g in gaps if g.priority.value == "CRITICAL")
        high_count = sum(1 for g in gaps if g.priority.value == "HIGH")

        missing = [g.text for g in gaps if g.type.value in ("MISSING_REQUIREMENT", "EXPERIENCE_GAP", "QUALIFICATION_GAP", "DOMAIN_GAP") and g.status == "MISSING"]
        partial = [g.text for g in gaps if g.status == "PARTIAL"]
        weak = [g.text for g in gaps if g.type.value == "WEAK_EVIDENCE"]

        return Analysis(
            context=context,
            scores=scores,
            strengths=top_strengths,
            gaps=gaps,
            missing_requirements=missing,
            partial_requirements=partial,
            weak_evidence=weak,
            recommendations=top_recommendations,
            categories=categories,
            requirements=requirements or [],
            summary=AnalysisSummary(
                primary_score=primary_score,
                score_type=score_type,
                strongest_area=strongest_area,
                weakest_area=weakest_area,
                critical_gap_count=critical_count,
                high_priority_gap_count=high_count,
            ),
            algorithm_versions=versions,
        )


def _strongest_weakest_category(categories: dict) -> tuple[str | None, str | None]:
    if not categories:
        return None, None
    ranked = sorted(categories.items(), key=lambda kv: kv[1].score, reverse=True)
    return ranked[0][0], ranked[-1][0]
