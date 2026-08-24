"""Target Profile Registry (spec §6, §25). A curated, versioned knowledge
base — never an LLM-invented profile. Base profiles are seeded from
target_profile_registry.json; this class only reads/merges them, it never
mutates the underlying data.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.modules.normalization import NormalizationService
from app.modules.target_profile.config import PROFILE_VERSION
from app.modules.target_profile.errors import DomainNotSupportedError, PositionNotSupportedError
from app.modules.target_profile.schemas import (
    CustomRequirements,
    DomainRef,
    EffectiveTargetProfile,
    PositionRef,
    TargetProfile,
    TargetProfileCategories,
)

_DATA_PATH = Path(__file__).parent / "data" / "target_profile_registry.json"


@lru_cache
def _load_registry_data() -> dict:
    return json.loads(_DATA_PATH.read_text())


def _merge_unique(*lists: list[str]) -> list[str]:
    """Case/whitespace-insensitive dedup (spec §20) — order-preserving,
    first occurrence wins."""
    seen: set[str] = set()
    merged: list[str] = []
    for items in lists:
        for item in items:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(item.strip())
    return merged


class TargetProfileRegistry:
    def __init__(self, normalization_service: NormalizationService | None = None):
        self._data = _load_registry_data()
        self._normalization = normalization_service or NormalizationService()

    @property
    def knowledge_version(self) -> str:
        return self._data["knowledge_version"]

    def list_positions(self) -> list[str]:
        return sorted(self._data["position_profiles"].keys())

    def list_domains(self) -> list[str]:
        return sorted(self._data["domain_profiles"].keys())

    def get_position_profile(self, canonical_position: str) -> dict | None:
        return self._data["position_profiles"].get(canonical_position)

    def get_domain_profile(self, canonical_domain: str) -> dict | None:
        return self._data["domain_profiles"].get(canonical_domain)

    def get_profile(self, raw_position: str, raw_domain: str | None = None) -> TargetProfile:
        """Resolves raw position/domain strings to canonical entities
        (reusing Phase 4's NormalizationService — spec §4-5) and returns
        the curated base profile. Raises PositionNotSupportedError /
        DomainNotSupportedError (spec §23-24) rather than silently mapping
        to an unrelated role/domain."""
        normalized_position = self._normalization.normalize_role(raw_position)
        canonical_position = normalized_position.canonical_role
        if canonical_position is None or self.get_position_profile(canonical_position) is None:
            raise PositionNotSupportedError(
                f"Position '{raw_position}' is not in the Target Profile registry.",
                details={"raw_position": raw_position},
            )

        canonical_domain = None
        domain_profile: dict = {}
        if raw_domain:
            normalized_domain = self._normalization.normalize_domain(raw_domain)
            canonical_domain = normalized_domain.canonical_domain
            if canonical_domain is None or self.get_domain_profile(canonical_domain) is None:
                raise DomainNotSupportedError(
                    f"Domain '{raw_domain}' is not in the Target Profile registry.",
                    details={"raw_domain": raw_domain},
                )
            domain_profile = self.get_domain_profile(canonical_domain) or {}

        position_profile = self.get_position_profile(canonical_position) or {}

        return TargetProfile(
            position=PositionRef(raw=raw_position, canonical=canonical_position),
            domain=DomainRef(raw=raw_domain, canonical=canonical_domain),
            core_skills=_merge_unique(position_profile.get("core_skills", []), domain_profile.get("core_skills", [])),
            technologies=_merge_unique(position_profile.get("technologies", []), domain_profile.get("technologies", [])),
            responsibilities=_merge_unique(
                position_profile.get("responsibilities", []), domain_profile.get("responsibilities", [])
            ),
            domain_knowledge=list(domain_profile.get("domain_knowledge", [])),
            experience_expectations=list(position_profile.get("experience_expectations", [])),
            preferred_skills=_merge_unique(
                position_profile.get("preferred_skills", []), domain_profile.get("preferred_skills", [])
            ),
            knowledge_version=self.knowledge_version,
            profile_version=PROFILE_VERSION,
        )

    def build_effective_profile(
        self,
        raw_position: str,
        raw_domain: str | None = None,
        custom_requirements: CustomRequirements | None = None,
    ) -> EffectiveTargetProfile:
        """Base Profile + Custom Requirements = Effective Target Profile
        (spec §10-11). The base profile is never mutated; custom items are
        merged on top (custom takes priority in the sense that it's always
        included, even if it duplicates a base item — dedup still applies
        so it isn't double-counted)."""
        base = self.get_profile(raw_position, raw_domain)
        custom = custom_requirements or CustomRequirements()

        effective = TargetProfileCategories(
            core_skills=_merge_unique(base.core_skills, custom.core_skills),
            technologies=_merge_unique(base.technologies, custom.technologies),
            responsibilities=_merge_unique(base.responsibilities, custom.responsibilities),
            domain_knowledge=_merge_unique(base.domain_knowledge, custom.domain_knowledge),
            experience_expectations=_merge_unique(base.experience_expectations, custom.experience_expectations),
            preferred_skills=_merge_unique(base.preferred_skills, custom.preferred_skills),
        )

        return EffectiveTargetProfile(base_profile=base, custom_requirements=custom, effective=effective)
