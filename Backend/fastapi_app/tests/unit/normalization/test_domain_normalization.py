from app.modules.normalization.domains import normalize_domain
from app.modules.normalization.schemas import NormalizationStatus


def test_financial_technology_resolves_to_fintech():
    r = normalize_domain("Financial Technology")
    assert r.canonical_domain == "FINTECH"


def test_domain_variants_map_to_the_same_canonical():
    variants = ["FinTech", "Financial Technology", "Financial Tech"]
    canonicals = {normalize_domain(v).canonical_domain for v in variants}
    assert canonicals == {"FINTECH"}


def test_domain_hierarchy_parent_is_exposed():
    r = normalize_domain("FinTech")
    assert r.parent_domain == "TECHNOLOGY"


def test_distinct_domains_stay_distinct():
    fintech = normalize_domain("FinTech").canonical_domain
    healthtech = normalize_domain("HealthTech").canonical_domain
    edtech = normalize_domain("EdTech").canonical_domain
    assert len({fintech, healthtech, edtech}) == 3


def test_unrecognized_domain_is_unknown():
    r = normalize_domain("Underwater Basket Weaving")
    assert r.canonical_domain is None
    assert r.normalization_status == NormalizationStatus.UNKNOWN
