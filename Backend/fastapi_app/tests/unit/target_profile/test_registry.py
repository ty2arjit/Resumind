"""Unit tests for TargetProfileRegistry (spec §32 cases 1-2, 5-11)."""

import pytest

from app.modules.target_profile.errors import DomainNotSupportedError, PositionNotSupportedError
from app.modules.target_profile.registry import TargetProfileRegistry
from app.modules.target_profile.schemas import CustomRequirements

_registry = TargetProfileRegistry()


# --- Case 1: known position ---

def test_known_position_resolves_profile():
    profile = _registry.get_profile("Backend Developer")
    assert profile.position.canonical == "BACKEND_SOFTWARE_ENGINEER"
    assert "Python" in profile.core_skills


# --- Case 2: known domain ---

def test_known_domain_adds_domain_knowledge():
    profile = _registry.get_profile("Backend Developer", "FinTech")
    assert profile.domain.canonical == "FINTECH"
    assert "payments" in profile.domain_knowledge


# --- Case 3: position normalization (spec §4) ---

@pytest.mark.parametrize(
    "raw", ["Backend Developer", "Backend Engineer", "Backend Software Engineer", "SDE Backend", "Server-side Engineer"]
)
def test_position_normalization_resolves_aliases(raw):
    profile = _registry.get_profile(raw)
    assert profile.position.canonical == "BACKEND_SOFTWARE_ENGINEER"


# --- Case 4: domain normalization (spec §5) ---

@pytest.mark.parametrize("raw", ["Financial Technology", "Financial Tech", "FinTech"])
def test_domain_normalization_resolves_aliases(raw):
    profile = _registry.get_profile("Backend Developer", raw)
    assert profile.domain.canonical == "FINTECH"


# --- Case 5: position + domain combination (spec §19) ---

def test_position_and_domain_combine():
    profile = _registry.get_profile("Backend Developer", "FinTech")
    # position-sourced
    assert "Python" in profile.core_skills
    # domain-sourced
    assert "payments" in profile.domain_knowledge
    # domain-added technology
    assert "PostgreSQL" in profile.technologies


# --- Case 6: duplicate requirement removal (spec §20) ---

def test_duplicate_technology_across_position_and_domain_is_not_repeated():
    profile = _registry.get_profile("Backend Developer", "FinTech")
    assert profile.technologies.count("PostgreSQL") == 1


# --- Case 7: custom requirements (spec §10-11) ---

def test_custom_requirements_are_added_and_preserved_separately():
    custom = CustomRequirements(technologies=["Kafka"], domain_knowledge=["payment gateways"])
    effective = _registry.build_effective_profile("Backend Developer", "FinTech", custom)
    assert "Kafka" in effective.effective.technologies
    assert "payment gateways" in effective.effective.domain_knowledge
    # base profile itself is untouched
    assert "Kafka" not in effective.base_profile.technologies
    assert effective.custom_requirements.technologies == ["Kafka"]


def test_custom_requirement_duplicating_base_is_not_double_counted():
    custom = CustomRequirements(technologies=["postgresql"])  # case-insensitive dup of base's "PostgreSQL"
    effective = _registry.build_effective_profile("Backend Developer", "FinTech", custom)
    assert effective.effective.technologies.count("PostgreSQL") == 1


# --- Case 8: unknown position (spec §24) ---

def test_unknown_position_raises_position_not_supported():
    with pytest.raises(PositionNotSupportedError) as exc_info:
        _registry.get_profile("Underwater Basket Weaver")
    assert exc_info.value.error_code == "POSITION_NOT_SUPPORTED"


# --- Case 9: unknown domain (spec §23) ---

def test_unknown_domain_raises_domain_not_supported():
    with pytest.raises(DomainNotSupportedError) as exc_info:
        _registry.get_profile("Backend Developer", "Underwater Domain")
    assert exc_info.value.error_code == "DOMAIN_NOT_SUPPORTED"


def test_position_alone_does_not_require_domain():
    profile = _registry.get_profile("Backend Developer")
    assert profile.domain.canonical is None
    assert profile.domain_knowledge == []


# --- Case 10: custom profile (effective profile without a domain) ---

def test_custom_profile_without_domain():
    effective = _registry.build_effective_profile(
        "Backend Developer", None, CustomRequirements(core_skills=["GraphQL"])
    )
    assert "GraphQL" in effective.effective.core_skills
    assert effective.effective.domain_knowledge == []


# --- Case 11: target profile versioning (spec §9) ---

def test_profile_has_knowledge_and_profile_versions():
    profile = _registry.get_profile("Backend Developer", "FinTech")
    assert profile.knowledge_version
    assert profile.profile_version == "TARGET_PROFILE_V1"


# --- Case 12: deterministic profile generation (spec §35) ---

def test_profile_generation_is_deterministic():
    profiles = [_registry.get_profile("Backend Developer", "FinTech") for _ in range(3)]
    assert len({tuple(sorted(p.core_skills)) for p in profiles}) == 1
    assert len({tuple(sorted(p.domain_knowledge)) for p in profiles}) == 1
