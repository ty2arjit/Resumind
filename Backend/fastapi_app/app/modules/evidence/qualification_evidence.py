"""Qualification evidence (spec §21) — wraps Phase 5's qualification
matcher into the Evidence Engine's own output shape."""

from app.modules.evidence.schemas import QualificationEvidence
from app.modules.matching.qualification import match_qualification
from app.modules.resume.schemas import EducationEntry


def build_qualification_evidence(
    requirement_degree: str | None, requirement_field: str | None, resume_education: list[EducationEntry]
) -> QualificationEvidence | None:
    if requirement_degree is None and requirement_field is None:
        return None

    signals = match_qualification(requirement_degree, requirement_field, resume_education)

    return QualificationEvidence(
        degree=signals.degree_evidence,
        field=signals.field_evidence,
        institution=resume_education[0].institution if resume_education else None,
        evidence_text=resume_education[0].raw_text if resume_education else None,
        matched=signals.matched,
        uncertain=signals.uncertain,
    )
