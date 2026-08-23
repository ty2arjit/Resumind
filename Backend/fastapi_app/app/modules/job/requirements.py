"""Requirement extraction, classification, and importance assignment
(spec §5-9, §16-19).

Deliberately conservative at every step: a candidate sentence only
becomes a Requirement if it carries a concrete signal (a technology
mention, an explicit requirement phrase, an experience-years pattern, a
degree/certification keyword, or a responsibility action verb) — generic
prose is dropped rather than turned into a meaningless requirement.
"""

import re

from app.models.enums import ImportanceLevel, RequirementType
from app.modules.common.bullets import is_bullet, strip_bullet
from app.modules.job.experience_requirements import extract_experience_requirement
from app.modules.job.operators import detect_operator
from app.modules.job.schemas import JDCanonicalSection, Requirement
from app.modules.resume.actions import extract_actions, leading_action
from app.modules.resume.technologies import extract_technologies
from app.modules.scoring.config import get_scoring_config

# Sections a requirement should never be extracted from — contextual/
# promotional content, not expectations placed on the candidate.
NON_REQUIREMENT_SECTIONS = {JDCanonicalSection.ABOUT_COMPANY, JDCanonicalSection.SUMMARY, JDCanonicalSection.BENEFITS}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

_REQUIREMENT_SIGNAL_RE = re.compile(
    r"\b(required|require|requires|requirement|must|mandatory|should have|preferred|"
    r"nice to have|bonus|plus|experience (?:with|in|of)|knowledge of|familiarity with|"
    r"proficien(?:cy|t) in|ability to|strong understanding of|excellent|skilled in|"
    r"degree|certification|certified|licen[sc]e|years?)\b",
    re.IGNORECASE,
)

_DEGREE_SIGNAL_RE = re.compile(
    r"\b(bachelor|master|b\.?\s?tech|m\.?\s?tech|phd|degree|diploma|certification|certified|licen[sc]e)\b",
    re.IGNORECASE,
)

_REQUIRED_WORDS_RE = re.compile(
    r"\b(required|require[sd]?|must have|must be|mandatory|should have|need to have)\b", re.IGNORECASE
)
_PREFERRED_WORDS_RE = re.compile(r"\b(preferred|nice to have|bonus|(?:is|are) a plus|good to have)\b", re.IGNORECASE)
_OPTIONAL_WORDS_RE = re.compile(r"\b(optional|not required)\b", re.IGNORECASE)

_CRITICAL_RE = re.compile(r"\bmandatory\b|^must have\b|^required:", re.IGNORECASE)

_DEDUP_STOPWORDS = {
    "experience", "with", "in", "of", "strong", "excellent", "solid", "good",
    "proven", "demonstrated", "proficiency", "proficient", "knowledge", "the",
    "a", "an", "and", "skills", "skill", "years", "year", "is", "are", "to",
}


def split_candidate_sentences(content_lines: list[str]) -> list[str]:
    """Bullets become one candidate each; non-bulleted paragraph lines are
    joined and split into sentences."""
    candidates: list[str] = []
    buffer: list[str] = []

    def flush_buffer():
        if buffer:
            joined = " ".join(buffer).strip()
            if joined:
                candidates.extend(p.strip() for p in _SENTENCE_SPLIT_RE.split(joined) if p.strip())
            buffer.clear()

    for line in content_lines:
        if is_bullet(line):
            flush_buffer()
            text = strip_bullet(line)
            if text:
                candidates.append(text)
        else:
            buffer.append(line.strip())

    flush_buffer()
    return candidates


def _is_meaningful(text: str, technologies: list[str], has_leading_action: bool) -> bool:
    if technologies:
        return True
    if _REQUIREMENT_SIGNAL_RE.search(text):
        return True
    if has_leading_action:
        return True
    return False


def _classify_type(
    section: JDCanonicalSection,
    technologies: list[str],
    experience_req,
    has_degree_signal: bool,
    has_leading_action: bool,
    text: str,
) -> RequirementType:
    if experience_req is not None:
        return RequirementType.EXPERIENCE
    if has_degree_signal:
        return RequirementType.QUALIFICATION
    if section == JDCanonicalSection.RESPONSIBILITIES and has_leading_action:
        return RequirementType.RESPONSIBILITY
    if technologies:
        if section == JDCanonicalSection.QUALIFICATIONS_PREFERRED or _PREFERRED_WORDS_RE.search(text):
            return RequirementType.PREFERRED_SKILL
        return RequirementType.SKILL
    if has_leading_action:
        return RequirementType.RESPONSIBILITY
    return RequirementType.OTHER


def _assign_importance(text: str, section: JDCanonicalSection) -> tuple[ImportanceLevel, float]:
    """Returns (importance, confidence_bonus) — the bonus reflects how
    directly the classification was signaled (explicit wording > section
    context > nothing)."""
    if _REQUIRED_WORDS_RE.search(text):
        return ImportanceLevel.REQUIRED, 0.2
    if _PREFERRED_WORDS_RE.search(text):
        return ImportanceLevel.PREFERRED, 0.2
    if _OPTIONAL_WORDS_RE.search(text):
        return ImportanceLevel.OPTIONAL, 0.2

    if section == JDCanonicalSection.QUALIFICATIONS_REQUIRED:
        return ImportanceLevel.REQUIRED, 0.1
    if section == JDCanonicalSection.QUALIFICATIONS_PREFERRED:
        return ImportanceLevel.PREFERRED, 0.1

    return ImportanceLevel.UNKNOWN, 0.0


def _is_critical(text: str, importance: ImportanceLevel) -> bool:
    if importance != ImportanceLevel.REQUIRED:
        return False
    return bool(_CRITICAL_RE.search(text.strip()))


def build_requirement(text: str, section: JDCanonicalSection, req_id: str) -> Requirement | None:
    """Returns None if `text` doesn't carry enough signal to be a
    meaningful requirement (spec §5) — callers should skip it, not force
    a low-quality entry."""
    technologies = extract_technologies(text)
    leading = leading_action(text)

    if not _is_meaningful(text, technologies, leading is not None):
        return None

    experience_req = extract_experience_requirement(text)
    has_degree_signal = bool(_DEGREE_SIGNAL_RE.search(text))

    req_type = _classify_type(section, technologies, experience_req, has_degree_signal, leading is not None, text)
    importance, importance_bonus = _assign_importance(text, section)
    critical = _is_critical(text, importance)

    has_concrete_entity = bool(technologies or experience_req or has_degree_signal)
    confidence = min(0.5 + importance_bonus + (0.15 if has_concrete_entity else 0.0), 0.97)

    weight = get_scoring_config().requirement_importance_weights.for_importance(importance)

    return Requirement(
        id=req_id,
        text=text,
        type=req_type,
        importance=importance,
        weight=weight,
        critical=critical,
        confidence=confidence,
        source_section=section,
        actions=extract_actions(text),
        technologies=technologies,
        experience=experience_req,
        operator=detect_operator(text),
    )


def normalize_for_dedup(text: str) -> str:
    """Token-set normalization so word-order/qualifier differences (e.g.
    "Experience with Python" vs "Strong Python experience") still collapse
    to the same key — deliberately looser than exact-text matching, but
    still far short of semantic deduplication (spec §19)."""
    # Deliberately excludes "." from the token class: a trailing sentence
    # period would otherwise stick to the last word ("python." /
    # "experience."), which defeats the stopword filter below since the
    # dotted and undotted forms no longer compare equal.
    words = re.findall(r"[a-zA-Z0-9+#]+", text.lower())
    significant = sorted(w for w in words if w not in _DEDUP_STOPWORDS and len(w) > 1)
    return " ".join(significant)


def find_duplicate_groups(requirements: list[Requirement]) -> list[list[Requirement]]:
    groups: dict[str, list[Requirement]] = {}
    for req in requirements:
        key = normalize_for_dedup(req.text)
        if not key:
            continue
        groups.setdefault(key, []).append(req)
    return [group for group in groups.values() if len(group) > 1]
