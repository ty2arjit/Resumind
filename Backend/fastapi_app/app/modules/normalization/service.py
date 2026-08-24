"""Centralized normalization service (spec §17-18).

This is the ONLY module the future matching engine (Phase 5) should
depend on for normalization — it must not implement its own alias logic,
mirroring how app.modules.embeddings.EmbeddingService is the sole seam
for embeddings (Phase 1's architecture principle applied here too).
"""

from typing import TYPE_CHECKING

from app.modules.normalization.actions import normalize_action
from app.modules.normalization.domains import normalize_domain
from app.modules.normalization.entities import normalize_skill
from app.modules.normalization.registry import get_skill_registry
from app.modules.normalization.roles import normalize_role
from app.modules.normalization.schemas import NormalizedAction, NormalizedDomain, NormalizedEntity, NormalizedRole, NormalizedSkillSet
from app.modules.resume.schemas import StructuredResume

if TYPE_CHECKING:
    from app.modules.job.schemas import StructuredJD


class NormalizationService:
    """Stateless — every method is a pure function of its input plus the
    (cached, versioned) knowledge registries. Safe to use as a singleton
    or to instantiate freely.
    """

    def normalize_entity(self, raw_value: str) -> NormalizedEntity:
        """Generic entry point; currently equivalent to normalize_skill()
        since skills/technologies are the only free-text entity category
        Phase 2/3 produce today. Kept distinct so future entity kinds
        (e.g. certifications) can be routed here without moving callers.
        """
        return normalize_skill(raw_value)

    def normalize_skill(self, raw_value: str) -> NormalizedEntity:
        return normalize_skill(raw_value)

    def normalize_entities(self, raw_values: list[str]) -> list[NormalizedEntity]:
        return [normalize_skill(v) for v in raw_values]

    def normalize_role(self, raw_role: str) -> NormalizedRole:
        return normalize_role(raw_role)

    def normalize_domain(self, raw_domain: str) -> NormalizedDomain:
        return normalize_domain(raw_domain)

    def normalize_action(self, raw_action: str) -> NormalizedAction:
        return normalize_action(raw_action)

    def normalize_resume(self, resume: StructuredResume) -> NormalizedSkillSet:
        """Normalizes every unique raw skill/technology mention found
        across a parsed resume (skills section + experience/project
        technologies + evidence technologies) — does not re-parse or
        touch the resume itself (spec §1: normalization is a separate
        layer from Phase 2's parser).
        """
        raw_mentions = _collect_resume_skill_mentions(resume)
        return self._build_skill_set(raw_mentions)

    def normalize_job_description(self, jd: "StructuredJD") -> NormalizedSkillSet:
        raw_mentions = _collect_jd_skill_mentions(jd)
        return self._build_skill_set(raw_mentions)

    def _build_skill_set(self, raw_mentions: list[str]) -> NormalizedSkillSet:
        registry = get_skill_registry()
        return NormalizedSkillSet(
            skills=[normalize_skill(v) for v in raw_mentions],
            knowledge_version=registry.knowledge_version,
        )


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: list[str] = []
    for v in values:
        if v not in seen:
            seen.append(v)
    return seen


def _collect_resume_skill_mentions(resume: StructuredResume) -> list[str]:
    mentions: list[str] = []
    for category in resume.skills:
        mentions.extend(category.items)
    for entry in resume.experience:
        mentions.extend(entry.technologies)
    for entry in resume.projects:
        mentions.extend(entry.technologies)
    for evidence in resume.evidence:
        mentions.extend(evidence.technologies)
    return _dedupe_preserve_order(mentions)


def _collect_jd_skill_mentions(jd: "StructuredJD") -> list[str]:
    mentions: list[str] = list(jd.skills)
    for requirement in jd.requirements:
        mentions.extend(requirement.technologies)
    return _dedupe_preserve_order(mentions)


def group_by_canonical(entities: list[NormalizedEntity]) -> dict[str, list[NormalizedEntity]]:
    """Spec §9 — e.g. {"Python": [NormalizedEntity("Python"), NormalizedEntity("Python3"), ...]}.
    Entities with no resolved canonical value (UNKNOWN/AMBIGUOUS) are
    grouped under their own raw_value instead of silently dropped.
    """
    groups: dict[str, list[NormalizedEntity]] = {}
    for entity in entities:
        key = entity.canonical_value or entity.raw_value
        groups.setdefault(key, []).append(entity)
    return groups
