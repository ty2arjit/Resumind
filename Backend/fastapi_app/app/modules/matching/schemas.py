"""Hybrid matching output schemas (spec Phase 5 §3, §20).

MatchStrength is reused from app.models.enums (the same enum the
Postgres `requirement_matches` table uses) — not redefined here.
"""

import enum

from pydantic import BaseModel, Field

from app.models.enums import MatchStrength


class EvidenceContext(str, enum.Enum):
    EXPERIENCE = "EXPERIENCE"
    PROJECT = "PROJECT"
    SKILLS = "SKILLS"
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    SUMMARY = "SUMMARY"
    OTHER = "OTHER"


class MatchableEvidence(BaseModel):
    """A single piece of resume evidence in the shape the matching engine
    operates on — built once per resume by evidence_index.py, reused
    across every requirement comparison rather than re-derived per call.
    """

    id: str
    text: str
    context: EvidenceContext
    technologies: list[str] = []
    actions: list[str] = []
    position: str | None = None


class MatchSignals(BaseModel):
    """Raw per-technique signals (spec §20) — never a final score.

    exact/canonical are None (not 0.0) when the requirement has no
    extractable technology to compare at all (e.g. a pure responsibility
    requirement like "Develop REST APIs") — "not applicable" must stay
    distinguishable from "applicable, but no match found", or fusion
    would structurally cap every non-technology requirement's score
    around 50% regardless of how strong its semantic/keyword evidence is.
    semantic is None when the embedding service is unavailable, for the
    same reason. keyword/tfidf/context always operate on text that's
    always present, so they're never None.
    """

    exact: float | None = 0.0
    canonical: float | None = 0.0
    keyword: float = 0.0
    tfidf: float = 0.0
    semantic: float | None = None
    context: float = 0.0


class MatchExplanation(BaseModel):
    """Structured (not natural-language) explainability data (spec §33)."""

    canonical_entity_match: bool = False
    canonical_value: str | None = None
    keyword_overlap: list[str] = []
    semantic_similarity: float | None = None
    evidence_section: str | None = None
    relevant_technologies: list[str] = []
    raw_evidence_text: str | None = None


class HybridMatchResult(BaseModel):
    """One requirement-evidence comparison result (spec §20). NOT an ATS
    score — a preliminary match-strength classification only."""

    requirement_id: str
    evidence_id: str | None = None
    signals: MatchSignals
    score: float = Field(ge=0.0, le=1.0)
    match_type: MatchStrength
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: MatchExplanation


class ResponsibilityMatchSignals(BaseModel):
    """spec §17."""

    action_signal: float = 0.0
    object_signal: float = 0.0
    technology_signal: float = 0.0
    semantic_signal: float | None = None


class ExperienceMatchSignals(BaseModel):
    """spec §18 — signals only, no penalty/score decision."""

    required_years: float | None = None
    detected_years: float | None = None
    confidence: float = 0.0
    context: str | None = None


class QualificationMatchSignals(BaseModel):
    """spec §19."""

    matched: bool = False
    degree_evidence: str | None = None
    field_evidence: str | None = None
    confidence: float = 0.0
    uncertain: bool = True
