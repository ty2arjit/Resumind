"""Deterministic message templates (spec §18) — presentation text kept
separate from recommendation-generation logic so the frontend can later
swap in localized/polished copy without touching the rules that decide
*whether* a recommendation fires."""

_TEMPLATES: dict[str, str] = {
    "MISSING_REQUIRED_SKILL": (
        "{text} is a required skill for this role but is not currently demonstrated in your resume. "
        "If you genuinely have this experience, add concrete evidence from a project, internship, or professional role."
    ),
    "MISSING_PREFERRED_SKILL": (
        "{text} is a preferred (not required) skill that is not currently demonstrated in your resume. "
        "If you have genuine experience with it, adding evidence could strengthen your application."
    ),
    "MISSING_RESPONSIBILITY": (
        "The resume does not currently show evidence of \"{text}\". "
        "If you have genuinely done this, describe it in an experience or project bullet."
    ),
    "MISSING_DOMAIN_KNOWLEDGE": (
        "\"{text}\" is domain knowledge expected for this role but is not currently demonstrated. "
        "If you have relevant exposure, add concrete evidence rather than just the keyword."
    ),
    "MISSING_QUALIFICATION": (
        "The qualification \"{text}\" could not be confirmed from your resume. "
        "If accurate, ensure your education section clearly states the degree and field."
    ),
    "STRENGTHEN_SKILL_EVIDENCE": (
        "\"{text}\" appears in your resume but is only weakly demonstrated. "
        "Strengthen it by describing where and how you used it in a project or experience bullet."
    ),
    "PARTIAL_REQUIREMENT": (
        "\"{text}\" is partially supported by your resume. Consider adding more specific, concrete evidence "
        "if you have it, so the match is unambiguous."
    ),
    "EXPERIENCE_SHORTFALL": (
        "The experience duration for \"{text}\" appears shorter than what's expected. "
        "If your actual experience is longer, ensure your dates and role descriptions are clear and complete."
    ),
    "EXPERIENCE_UNKNOWN": (
        "Experience duration for \"{text}\" could not be reliably determined from the available dates. "
        "Consider clarifying your employment dates."
    ),
    "IMPROVE_DOMAIN_EVIDENCE": (
        "Your resume shows limited demonstrated evidence for the \"{text}\" domain area. "
        "If you have genuine domain experience, add specific examples rather than relying on generic keywords."
    ),
    "PARSING_WARNING": (
        "Review the resume formatting — the parser detected a possible issue ({finding_key}) that may affect "
        "how ATS systems read your resume."
    ),
    "IMPROVE_STRUCTURE": (
        "Your resume's section structure could be clearer ({finding_key}). Consider organizing content into "
        "clearly labeled, consistent sections."
    ),
    "REDUCE_KEYWORD_REPETITION": (
        "Some content appears to be repeated or duplicated ({finding_key}). Removing duplication can improve "
        "both readability and ATS parsing."
    ),
    "ADD_METRIC_WHERE_ACCURATE": (
        "Several bullets describe tasks without a measurable outcome. Where accurate, add a concrete metric "
        "or result to strengthen this evidence."
    ),
    "CLARIFY_DATES": (
        "Some dates in your resume could not be reliably interpreted or are inconsistently ordered ({finding_key}). "
        "Review and clarify them where possible."
    ),
    "IMPROVE_CONTACT_INFO": (
        "Your resume is missing some core contact information. Adding a name and email address helps recruiters "
        "and ATS systems identify and reach you."
    ),
}


def render_message(message_key: str, **params: str) -> str:
    template = _TEMPLATES.get(message_key)
    if template is None:
        return message_key
    try:
        return template.format(**params)
    except KeyError:
        return template
