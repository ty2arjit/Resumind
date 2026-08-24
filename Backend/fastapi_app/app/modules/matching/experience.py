"""Experience matching (spec §18). Produces signals only — no scoring
penalty/decision. Never fabricates a duration when dates are unreliable."""

from app.modules.matching.schemas import ExperienceMatchSignals
from app.modules.normalization import NormalizationService
from app.modules.resume.schemas import ExperienceEntry

_service = NormalizationService()


def _shares_technology(context_technologies: list[str], entry_technologies: list[str]) -> bool:
    context_canonicals = {
        r.canonical_value for r in (_service.normalize_skill(t) for t in context_technologies) if r.canonical_value
    }
    entry_canonicals = {
        r.canonical_value for r in (_service.normalize_skill(t) for t in entry_technologies) if r.canonical_value
    }
    return bool(context_canonicals & entry_canonicals)


def match_experience(
    required_years: float | None,
    context_technologies: list[str],
    context_text: str | None,
    resume_experience: list[ExperienceEntry],
) -> ExperienceMatchSignals:
    if required_years is None:
        return ExperienceMatchSignals(confidence=0.0, context=context_text)

    relevant_entries = [
        entry
        for entry in resume_experience
        if entry.dates is not None and entry.dates.duration_months is not None
        and (not context_technologies or _shares_technology(context_technologies, entry.technologies))
    ]

    if relevant_entries:
        total_months = sum(entry.dates.duration_months for entry in relevant_entries)
        return ExperienceMatchSignals(
            required_years=required_years,
            detected_years=round(total_months / 12, 1),
            confidence=0.9,
            context=context_text,
        )

    # No relevant entry with a reliable duration. Distinguish "genuinely
    # no matching experience" from "dates present but unreliable" —
    # both return detected_years=None (never fabricated), but confidence
    # differs so the caller can tell UNKNOWN apart from MISSING.
    if not resume_experience:
        # No experience section/dates at all — genuinely unknown, not a
        # confident absence of this specific technology.
        confidence = 0.3
    else:
        has_any_relevant_entry = any(
            not context_technologies or _shares_technology(context_technologies, entry.technologies)
            for entry in resume_experience
        )
        confidence = 0.3 if has_any_relevant_entry else 0.75
    return ExperienceMatchSignals(required_years=required_years, detected_years=None, confidence=confidence, context=context_text)
