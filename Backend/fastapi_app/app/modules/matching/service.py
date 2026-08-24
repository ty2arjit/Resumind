"""MatchingService — the single entry point the future Evidence Engine
(Phase 6) and everything after it should depend on (spec §27).

Batches TF-IDF and embedding computation once per requirement across its
whole candidate pool, rather than per-pair, per spec §26 performance
guidance.
"""

from app.models.enums import MatchStrength
from app.modules.matching.canonical import canonical_signal, is_known_technology_mismatch
from app.modules.matching.context import context_signal
from app.modules.matching.exact import exact_signal
from app.modules.matching.experience import match_experience as _match_experience
from app.modules.matching.fusion import classify_match_strength, fuse_signals
from app.modules.matching.keyword import keyword_signal
from app.modules.matching.qualification import match_qualification as _match_qualification
from app.modules.matching.responsibility import match_responsibility as _match_responsibility
from app.modules.matching.schemas import (
    ExperienceMatchSignals,
    HybridMatchResult,
    MatchableEvidence,
    MatchExplanation,
    MatchSignals,
    QualificationMatchSignals,
    ResponsibilityMatchSignals,
)
from app.modules.matching.semantic import SemanticMatcher
from app.modules.matching.tfidf_matcher import TfidfMatcher
from app.modules.resume.schemas import EducationEntry, ExperienceEntry
from app.modules.scoring.config import get_scoring_config

_STRENGTH_RANK = {
    MatchStrength.MISSING: 0,
    MatchStrength.WEAK: 1,
    MatchStrength.PARTIAL: 2,
    MatchStrength.STRONG: 3,
    MatchStrength.VERY_STRONG: 4,
}


class MatchingService:
    def __init__(self):
        self._tfidf = TfidfMatcher()
        self._semantic = SemanticMatcher()

    def match_entity(self, requirement_technologies: list[str], evidence: MatchableEvidence) -> MatchSignals:
        """Level 1 — entity-only signals (exact + canonical), spec §3."""
        exact = exact_signal(requirement_technologies, evidence)
        canonical, _ = canonical_signal(requirement_technologies, evidence)
        return MatchSignals(exact=exact, canonical=canonical, context=context_signal(evidence))

    def match_evidence(
        self, requirement_id: str, requirement_text: str, requirement_technologies: list[str], evidence: MatchableEvidence
    ) -> HybridMatchResult:
        """Level 2 — full hybrid match for a single requirement/evidence
        pair. Prefer retrieve_candidates() when comparing against many
        evidence items — that batches TF-IDF/embeddings; this computes
        them one at a time and is meant for ad hoc/single-pair use."""
        tfidf_scores = self._tfidf.similarity(requirement_text, [evidence.text])
        semantic_scores = self._semantic.similarity(requirement_text, [evidence.text])
        return self._build_result(
            requirement_id, requirement_text, requirement_technologies, evidence, tfidf_scores[0], semantic_scores[0]
        )

    def retrieve_candidates(
        self,
        requirement_id: str,
        requirement_text: str,
        requirement_technologies: list[str],
        evidence_pool: list[MatchableEvidence],
        top_k: int | None = None,
    ) -> list[HybridMatchResult]:
        """spec §24-25 — ranks the whole evidence pool against one
        requirement and returns the top-K. Never fabricates evidence: if
        the pool is empty, returns an empty list."""
        if not evidence_pool:
            return []

        top_k = top_k if top_k is not None else get_scoring_config().matching.top_k_candidates

        evidence_texts = [e.text for e in evidence_pool]
        tfidf_scores = self._tfidf.similarity(requirement_text, evidence_texts)
        semantic_scores = self._semantic.similarity(requirement_text, evidence_texts)

        results = [
            self._build_result(requirement_id, requirement_text, requirement_technologies, evidence, tfidf, semantic)
            for evidence, tfidf, semantic in zip(evidence_pool, tfidf_scores, semantic_scores)
        ]

        # Deterministic ordering (spec §32): primary key is the fused
        # score, tie-broken by evidence id — evidence_index.py assigns
        # ids in a stable, resume-order sequence.
        results.sort(key=lambda r: (-_STRENGTH_RANK[r.match_type], -r.score, -r.confidence, r.evidence_id or ""))
        return results[:top_k]

    def match_responsibility(
        self, requirement_text: str, evidence: MatchableEvidence, semantic_signal: float | None
    ) -> ResponsibilityMatchSignals:
        return _match_responsibility(requirement_text, evidence, semantic_signal)

    def match_experience(
        self,
        required_years: float | None,
        context_technologies: list[str],
        context_text: str | None,
        resume_experience: list[ExperienceEntry],
    ) -> ExperienceMatchSignals:
        return _match_experience(required_years, context_technologies, context_text, resume_experience)

    def match_qualification(
        self, requirement_degree: str | None, requirement_field: str | None, resume_education: list[EducationEntry]
    ) -> QualificationMatchSignals:
        return _match_qualification(requirement_degree, requirement_field, resume_education)

    def _build_result(
        self,
        requirement_id: str,
        requirement_text: str,
        requirement_technologies: list[str],
        evidence: MatchableEvidence,
        tfidf: float,
        semantic: float | None,
    ) -> HybridMatchResult:
        exact = exact_signal(requirement_technologies, evidence)
        canonical, canonical_value = canonical_signal(requirement_technologies, evidence)
        keyword, overlap = keyword_signal(requirement_text, evidence.text)
        context = context_signal(evidence)

        signals = MatchSignals(exact=exact, canonical=canonical, keyword=keyword, tfidf=tfidf, semantic=semantic, context=context)
        fused_score, confidence = fuse_signals(signals)
        match_type = classify_match_strength(fused_score)

        # Hard guardrail (spec §6/§16): known distinct technologies must
        # never be rescued into a strong match by semantic similarity
        # alone, regardless of the fused score. Caps both the
        # classification and the underlying score so a consumer reading
        # `score` directly (e.g. Phase 6's relevance signal) can't see a
        # misleadingly high number alongside a capped match_type.
        if is_known_technology_mismatch(requirement_technologies, evidence) and _STRENGTH_RANK[match_type] > _STRENGTH_RANK[MatchStrength.WEAK]:
            match_type = MatchStrength.WEAK
            weak_ceiling = get_scoring_config().match_strength_thresholds.partial
            fused_score = min(fused_score, weak_ceiling - 1e-6)

        explanation = MatchExplanation(
            canonical_entity_match=bool(canonical),
            canonical_value=canonical_value,
            keyword_overlap=overlap,
            semantic_similarity=semantic,
            evidence_section=evidence.context.value,
            relevant_technologies=evidence.technologies,
            raw_evidence_text=evidence.text,
        )

        return HybridMatchResult(
            requirement_id=requirement_id,
            evidence_id=evidence.id,
            signals=signals,
            score=fused_score,
            match_type=match_type,
            confidence=confidence,
            explanation=explanation,
        )
