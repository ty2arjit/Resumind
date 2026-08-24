"""Loads the normalization knowledge sources (spec §6, §19) and builds the
lookup indices the pipeline needs. Centralized here — no other module
should read these JSON files directly or hardcode an alias (spec §6:
"Do NOT scatter aliases throughout parser or matching code").
"""

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from app.modules.normalization.schemas import EntityType
from app.modules.normalization.text_utils import formatting_key

_DATA_DIR = Path(__file__).parent / "data"


@dataclass
class SkillRegistry:
    knowledge_version: str
    canonical_types: dict[str, EntityType]  # canonical_name -> entity_type
    alias_index: dict[str, str]  # lowercase alias/canonical -> canonical_name
    formatting_index: dict[str, str]  # formatting_key -> canonical_name (collision-safe)
    ambiguous_terms: dict[str, str]  # lowercase term -> reason


@dataclass
class RoleRegistry:
    knowledge_version: str
    parent_of: dict[str, str | None]  # canonical_role -> parent_role
    alias_index: dict[str, str]
    formatting_index: dict[str, str]


@dataclass
class DomainRegistry:
    knowledge_version: str
    parent_of: dict[str, str | None]
    alias_index: dict[str, str]
    formatting_index: dict[str, str]


@dataclass
class ActionRegistry:
    knowledge_version: str
    canonical_actions: set[str]
    mappings: dict[str, str]  # lowercase raw action -> canonical action


def _build_formatting_index(entries: dict[str, list[str]]) -> dict[str, str]:
    """entries: canonical -> [canonical, *aliases]. Returns formatting_key
    -> canonical, EXCLUDING any key two different canonicals would both
    produce — an accidental collision must never silently pick a winner
    (spec §26: prefer Unknown over incorrectly normalized).
    """
    key_to_canonicals: dict[str, set[str]] = {}
    for canonical, strings in entries.items():
        for s in strings:
            key = formatting_key(s)
            if not key:
                continue
            key_to_canonicals.setdefault(key, set()).add(canonical)

    return {key: next(iter(canonicals)) for key, canonicals in key_to_canonicals.items() if len(canonicals) == 1}


@lru_cache
def get_skill_registry() -> SkillRegistry:
    data = json.loads((_DATA_DIR / "skill_aliases.json").read_text())
    canonical_types: dict[str, EntityType] = {}
    alias_index: dict[str, str] = {}
    formatting_entries: dict[str, list[str]] = {}

    for entity in data["entities"]:
        canonical = entity["canonical_name"]
        canonical_types[canonical] = EntityType(entity["entity_type"])
        alias_index[canonical.lower()] = canonical
        strings = [canonical]
        for alias in entity["aliases"]:
            alias_index[alias.lower()] = canonical
            strings.append(alias)
        formatting_entries[canonical] = strings

    ambiguous_data = json.loads((_DATA_DIR / "ambiguous_terms.json").read_text())
    ambiguous_terms = {t["term"].lower(): t["reason"] for t in ambiguous_data["terms"]}

    return SkillRegistry(
        knowledge_version=data["knowledge_version"],
        canonical_types=canonical_types,
        alias_index=alias_index,
        formatting_index=_build_formatting_index(formatting_entries),
        ambiguous_terms=ambiguous_terms,
    )


@lru_cache
def get_role_registry() -> RoleRegistry:
    data = json.loads((_DATA_DIR / "role_taxonomy.json").read_text())
    parent_of: dict[str, str | None] = {}
    alias_index: dict[str, str] = {}
    formatting_entries: dict[str, list[str]] = {}

    for role in data["roles"]:
        canonical = role["canonical_role"]
        parent_of[canonical] = role["parent_role"]
        strings = [canonical]
        for alias in role["aliases"]:
            alias_index[alias.lower()] = canonical
            strings.append(alias)
        formatting_entries[canonical] = strings

    return RoleRegistry(
        knowledge_version=data["knowledge_version"],
        parent_of=parent_of,
        alias_index=alias_index,
        formatting_index=_build_formatting_index(formatting_entries),
    )


@lru_cache
def get_domain_registry() -> DomainRegistry:
    data = json.loads((_DATA_DIR / "domain_taxonomy.json").read_text())
    parent_of: dict[str, str | None] = {}
    alias_index: dict[str, str] = {}
    formatting_entries: dict[str, list[str]] = {}

    for domain in data["domains"]:
        canonical = domain["canonical_domain"]
        parent_of[canonical] = domain["parent_domain"]
        strings = [canonical]
        for alias in domain["aliases"]:
            alias_index[alias.lower()] = canonical
            strings.append(alias)
        formatting_entries[canonical] = strings

    return DomainRegistry(
        knowledge_version=data["knowledge_version"],
        parent_of=parent_of,
        alias_index=alias_index,
        formatting_index=_build_formatting_index(formatting_entries),
    )


@lru_cache
def get_action_registry() -> ActionRegistry:
    data = json.loads((_DATA_DIR / "action_canonical_map.json").read_text())
    mappings = {raw.lower(): canonical for raw, canonical in data["mappings"].items()}
    return ActionRegistry(
        knowledge_version=data["knowledge_version"],
        canonical_actions=set(data["canonical_actions"]),
        mappings=mappings,
    )
