"""Experience duration evidence (spec §20) — wraps Phase 5's experience
matcher into the Evidence Engine's own output shape; no duplicate date
logic."""

from app.modules.evidence.schemas import ExperienceEvidence
from app.modules.matching.experience import match_experience
from app.modules.resume.schemas import ExperienceEntry


def build_experience_evidence(
    required_years: float | None,
    context_technologies: list[str],
    context_text: str | None,
    resume_experience: list[ExperienceEntry],
) -> ExperienceEvidence | None:
    if required_years is None:
        return None

    signals = match_experience(required_years, context_technologies, context_text, resume_experience)

    supporting = [
        f"{entry.role or 'Role'} at {entry.organization or 'Unknown organization'}"
        + (f" ({round(entry.dates.duration_months / 12, 1)} years)" if entry.dates and entry.dates.duration_months else "")
        for entry in resume_experience
        if not context_technologies or set(context_technologies) & set(entry.technologies)
    ]

    return ExperienceEvidence(
        required_years=signals.required_years,
        detected_relevant_years=signals.detected_years,
        date_confidence=signals.confidence,
        supporting_experience=supporting,
    )
