"""EvidenceService — the single entry point for requirement-evidence
retrieval (spec Phase 6). Reuses Phase 5's MatchingService for all
matching computation; owns selecting, ranking, deduplicating, and
aggregating evidence on top of it.
"""

from app.models.enums import MatchStrength
from app.modules.evidence.aggregation import aggregate_evidence_strength, evidence_diversity
from app.modules.evidence.dedup import deduplicate
from app.modules.evidence.experience_evidence import build_experience_evidence
from app.modules.evidence.index import build_evidence_pool
from app.modules.evidence.qualification_evidence import build_qualification_evidence
from app.modules.evidence.quality import build_quality_signals
from app.modules.evidence.ranking import rank_by_evidence_hierarchy
from app.modules.evidence.schemas import EvidenceItem, EvidenceSourceType, RankedEvidence, RequirementEvidenceResult
from app.modules.evidence.strength import classify_evidence_strength
from app.modules.matching.schemas import EvidenceContext, MatchableEvidence
from app.modules.matching.service import MatchingService
from app.modules.resume.schemas import StructuredResume
from app.modules.scoring.config import get_scoring_config

# EvidenceSourceType (this module) is a finer-grained taxonomy than
# Phase 5's EvidenceContext (spec §4 vs §15's smaller list) — this is an
# explicit translation between the two, not a self-mapping.
_SOURCE_TYPE_TO_MATCH_CONTEXT: dict[EvidenceSourceType, EvidenceContext] = {
    EvidenceSourceType.EXPERIENCE_BULLET: EvidenceContext.EXPERIENCE,
    EvidenceSourceType.PROJECT_BULLET: EvidenceContext.PROJECT,
    EvidenceSourceType.SKILLS_SECTION: EvidenceContext.SKILLS,
    EvidenceSourceType.EDUCATION: EvidenceContext.EDUCATION,
    EvidenceSourceType.CERTIFICATION: EvidenceContext.CERTIFICATION,
    EvidenceSourceType.SUMMARY: EvidenceContext.SUMMARY,
    EvidenceSourceType.ACHIEVEMENT: EvidenceContext.OTHER,
    EvidenceSourceType.LEADERSHIP: EvidenceContext.OTHER,
    EvidenceSourceType.OTHER: EvidenceContext.OTHER,
}


class EvidenceService:
    def __init__(self, matching_service: MatchingService | None = None):
        self._matching = matching_service or MatchingService()

    def retrieve_requirement_evidence(
        self,
        requirement_id: str,
        requirement_text: str,
        requirement_technologies: list[str],
        resume: StructuredResume,
        required_years: float | None = None,
        experience_context_technologies: list[str] | None = None,
        experience_context_text: str | None = None,
        requirement_degree: str | None = None,
        requirement_field: str | None = None,
        top_k: int | None = None,
    ) -> RequirementEvidenceResult:
        pool = build_evidence_pool(resume)
        pool, dedup_warnings = deduplicate(pool)

        top_k = top_k if top_k is not None else get_scoring_config().evidence_aggregation.top_k_evidence

        if not pool:
            return RequirementEvidenceResult(
                requirement_id=requirement_id,
                match_result=MatchStrength.UNKNOWN,
                warnings=["No resume evidence available to search."],
            )

        matchable_by_id = {item.id: self._to_matchable(item) for item in pool}
        item_by_id = {item.id: item for item in pool}

        # Cast a wider net than the final top_k: Phase 5's own ranking is
        # relevance-only, so a contextually strong bullet that scores
        # slightly lower on raw relevance (e.g. a longer, more complex
        # sentence vs. a short exact-phrase skills mention) must not be
        # excluded before rank_by_evidence_hierarchy() below gets a chance
        # to weigh context back in.
        candidate_k = min(len(pool), max(top_k * 3, get_scoring_config().matching.top_k_candidates))
        match_results = self._matching.retrieve_candidates(
            requirement_id, requirement_text, requirement_technologies, list(matchable_by_id.values()), top_k=candidate_k
        )

        ranked: list[RankedEvidence] = []
        for match_result in match_results:
            item = item_by_id[match_result.evidence_id]
            matchable = matchable_by_id[match_result.evidence_id]
            signals = build_quality_signals(requirement_text, match_result, item, matchable)
            ranked.append(
                RankedEvidence(
                    evidence_id=item.id,
                    text=item.text,
                    section=item.section,
                    position=item.position,
                    strength=classify_evidence_strength(signals.relevance),
                    signals=signals,
                )
            )

        ranked = rank_by_evidence_hierarchy(ranked)[:top_k]
        aggregated_strength = aggregate_evidence_strength(ranked)
        diversity = evidence_diversity(ranked)
        # The requirement's overall match classification must reflect the
        # BEST evidence found, not whichever item ranked #1 for display
        # purposes. rank_by_evidence_hierarchy() promotes items with
        # strong context (e.g. an experience bullet) ahead of a bare
        # skills-list mention even when the mention's own relevance is
        # higher — correct for presentation ("show the richer evidence
        # first"), but using that #1 item's raw-relevance EvidenceStrength
        # here would let genuinely stronger evidence elsewhere in the
        # ranked list get silently outvoted, producing the paradox of a
        # richer resume classifying *worse* than a sparser one (caught by
        # Phase 13's monotonicity evaluation — see docs/EVALUATION_REPORT.md).
        match_result_status = (
            _evidence_strength_to_match_strength(_strongest(ranked).strength) if ranked else MatchStrength.MISSING
        )

        experience_evidence = build_experience_evidence(
            required_years, experience_context_technologies or [], experience_context_text, resume.experience
        )
        qualification_evidence = build_qualification_evidence(requirement_degree, requirement_field, resume.education)

        return RequirementEvidenceResult(
            requirement_id=requirement_id,
            match_result=match_result_status,
            evidence=ranked,
            aggregated_evidence_strength=aggregated_strength,
            evidence_diversity=diversity,
            experience=experience_evidence,
            qualification=qualification_evidence,
            warnings=dedup_warnings,
        )

    @staticmethod
    def _to_matchable(item: EvidenceItem) -> MatchableEvidence:
        return MatchableEvidence(
            id=item.id,
            text=item.text,
            context=_SOURCE_TYPE_TO_MATCH_CONTEXT.get(item.section, EvidenceContext.OTHER),
            technologies=item.technologies,
            actions=item.actions,
            position=item.position,
        )


_EVIDENCE_STRENGTH_RANK = {
    "MISSING": 0,
    "UNKNOWN": 0,
    "WEAK": 1,
    "MODERATE": 2,
    "STRONG": 3,
    "VERY_STRONG": 4,
}


def _strongest(ranked: list[RankedEvidence]) -> RankedEvidence:
    return max(ranked, key=lambda item: _EVIDENCE_STRENGTH_RANK[item.strength.value])


def _evidence_strength_to_match_strength(strength) -> MatchStrength:
    return {
        "MISSING": MatchStrength.MISSING,
        "WEAK": MatchStrength.WEAK,
        "MODERATE": MatchStrength.PARTIAL,
        "STRONG": MatchStrength.STRONG,
        "VERY_STRONG": MatchStrength.VERY_STRONG,
        "UNKNOWN": MatchStrength.UNKNOWN,
    }[strength.value]
