from app.modules.normalization.roles import normalize_role
from app.modules.normalization.schemas import NormalizationStatus


def test_backend_developer_resolves_to_canonical_backend_role():
    r = normalize_role("Backend Developer")
    assert r.canonical_role == "BACKEND_SOFTWARE_ENGINEER"
    assert r.normalization_status == NormalizationStatus.RESOLVED


def test_role_variants_map_to_the_same_canonical():
    variants = ["Backend Developer", "Backend Engineer", "Backend Software Engineer", "Server-side Developer"]
    canonicals = {normalize_role(v).canonical_role for v in variants}
    assert canonicals == {"BACKEND_SOFTWARE_ENGINEER"}


def test_role_hierarchy_parent_is_exposed():
    r = normalize_role("Backend Developer")
    assert r.parent_role == "SOFTWARE_ENGINEER"


def test_distinct_role_families_stay_distinct():
    backend = normalize_role("Backend Developer").canonical_role
    frontend = normalize_role("Frontend Developer").canonical_role
    devops = normalize_role("DevOps Engineer").canonical_role
    assert len({backend, frontend, devops}) == 3


def test_unrecognized_role_is_unknown():
    r = normalize_role("Chief Vibes Officer")
    assert r.canonical_role is None
    assert r.normalization_status == NormalizationStatus.UNKNOWN


def test_case_insensitive_match():
    assert normalize_role("backend developer").canonical_role == "BACKEND_SOFTWARE_ENGINEER"
