from app.modules.normalization import NormalizationService


def test_normalize_entities_batch():
    svc = NormalizationService()
    results = svc.normalize_entities(["Python", "Postgres", "Docker"])
    assert [r.canonical_value for r in results] == ["Python", "PostgreSQL", "Docker"]


def test_service_methods_are_deterministic_across_calls():
    svc = NormalizationService()
    first = svc.normalize_skill("ReactJS")
    second = svc.normalize_skill("ReactJS")
    assert first == second


def test_normalize_entity_matches_normalize_skill():
    svc = NormalizationService()
    assert svc.normalize_entity("Postgres") == svc.normalize_skill("Postgres")
