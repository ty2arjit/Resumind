"""Qualification matching (spec §19). Deliberately conservative — only a
handful of well-established degree-level equivalences, no aggressive
academic-equivalence inference. "Or related field" wording is treated as
explicitly permissive since the JD itself said so, not because the
matcher invented equivalence.
"""

from app.modules.matching.schemas import QualificationMatchSignals
from app.modules.resume.schemas import EducationEntry

_DEGREE_LEVELS = {
    "bachelor": {"bachelor", "bachelor's", "bachelors", "b.tech", "btech", "b.e", "be", "b.sc", "bsc", "bca", "bba"},
    "master": {"master", "master's", "masters", "m.tech", "mtech", "m.e", "me", "m.sc", "msc", "mca", "mba"},
    "doctorate": {"phd", "ph.d", "doctorate"},
}


def _degree_level(degree: str | None) -> str | None:
    if not degree:
        return None
    normalized = degree.lower().strip(" .")
    for level, variants in _DEGREE_LEVELS.items():
        if normalized in variants:
            return level
    return None


def _field_relates(requirement_field: str | None, resume_field: str | None) -> bool | None:
    if requirement_field is None:
        return None
    if "related" in requirement_field.lower():
        return True  # the JD itself said "or related field" — not an invented equivalence
    if resume_field is None:
        return None
    return requirement_field.strip().lower() in resume_field.strip().lower() or resume_field.strip().lower() in requirement_field.strip().lower()


def match_qualification(
    requirement_degree: str | None, requirement_field: str | None, resume_education: list[EducationEntry]
) -> QualificationMatchSignals:
    if not resume_education:
        return QualificationMatchSignals(matched=False, confidence=0.0, uncertain=True)

    requirement_level = _degree_level(requirement_degree)

    for entry in resume_education:
        entry_level = _degree_level(entry.degree)
        degree_matches = requirement_level is None or (entry_level is not None and entry_level == requirement_level)
        field_relation = _field_relates(requirement_field, entry.field)
        field_matches = field_relation is not False  # True or None (uncertain) both allow a match

        if degree_matches and field_matches and (requirement_level is not None or field_relation):
            return QualificationMatchSignals(
                matched=True,
                degree_evidence=entry.degree,
                field_evidence=entry.field,
                confidence=0.85 if field_relation else 0.6,
                uncertain=field_relation is None,
            )

    best = resume_education[0]
    return QualificationMatchSignals(
        matched=False,
        degree_evidence=best.degree,
        field_evidence=best.field,
        confidence=0.35,
        uncertain=True,
    )
