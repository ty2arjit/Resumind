"""ScoringService — the single entry point for deterministic ATS
Alignment scoring (spec Phase 7 §29). Consumes Phase 2-6 outputs; never
reimplements parsing, normalization, matching, or evidence retrieval.
"""

from app.modules.embeddings import get_embedding_service
from app.modules.evidence import EvidenceService
from app.modules.job.qualifications import build_qualifications
from app.modules.job.schemas import StructuredJD
from app.modules.normalization import NormalizationService
from app.modules.resume.schemas import StructuredResume
from app.modules.scoring.ats_engine import calculate_ats_score, calculate_contributions, normalize_active_category_weights
from app.modules.scoring.category_scoring import mark_duplicates, score_categories
from app.modules.scoring.config import ALGORITHM_VERSION, get_scoring_config
from app.modules.scoring.requirement_scoring import score_requirement
from app.modules.scoring.schemas import ScoreBreakdown


class ScoringService:
    def __init__(self, evidence_service: EvidenceService | None = None, normalization_service: NormalizationService | None = None):
        self._evidence = evidence_service or EvidenceService()
        self._normalization = normalization_service or NormalizationService()

    def calculate_ats_alignment(self, jd: StructuredJD, resume: StructuredResume) -> ScoreBreakdown:
        normalized_resume = self._normalization.normalize_resume(resume)
        resume_canonical_skills = {e.canonical_value for e in normalized_resume.skills if e.canonical_value}
        qualification_by_text = {q.text: q for q in build_qualifications(jd.requirements)}

        requirement_scores = []
        for requirement in jd.requirements:
            qualification_entry = qualification_by_text.get(requirement.text)
            evidence_result = self._evidence.retrieve_requirement_evidence(
                requirement.id,
                requirement.text,
                requirement.technologies,
                resume,
                required_years=requirement.experience.min_years if requirement.experience else None,
                experience_context_technologies=requirement.technologies,
                experience_context_text=requirement.experience.context if requirement.experience else None,
                requirement_degree=qualification_entry.degree if qualification_entry else None,
                requirement_field=qualification_entry.field if qualification_entry else None,
            )
            requirement_scores.append(score_requirement(requirement, evidence_result, resume_canonical_skills))

        mark_duplicates(jd.requirements, requirement_scores)
        category_results = score_categories(requirement_scores)
        category_results = normalize_active_category_weights(category_results)
        calculate_contributions(requirement_scores, category_results)
        ats_alignment = calculate_ats_score(category_results)

        # model_version is set at construction time (not on first embed
        # call), so this never raises even before any embedding has run.
        embedding_model_version = get_embedding_service().model_version

        return ScoreBreakdown(
            ats_alignment=ats_alignment,
            categories={category.value: result for category, result in category_results.items()},
            requirements=requirement_scores,
            algorithm_version=ALGORITHM_VERSION,
            scoring_config_version=get_scoring_config().version,
            knowledge_version=normalized_resume.knowledge_version,
            embedding_model_version=embedding_model_version,
        )
