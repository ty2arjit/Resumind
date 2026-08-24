from app.modules.matching.canonical import canonical_signal, is_known_technology_mismatch
from app.modules.matching.schemas import EvidenceContext, MatchableEvidence


def _evidence(technologies):
    return MatchableEvidence(id="ev_1", text="x", context=EvidenceContext.EXPERIENCE, technologies=technologies)


def test_postgres_alias_matches_postgresql():
    signal, canonical = canonical_signal(["PostgreSQL"], _evidence(["Postgres"]))
    assert signal == 1.0
    assert canonical == "PostgreSQL"


def test_reactjs_matches_react():
    signal, canonical = canonical_signal(["React"], _evidence(["ReactJS"]))
    assert signal == 1.0


def test_docker_and_kubernetes_do_not_match():
    signal, canonical = canonical_signal(["Kubernetes"], _evidence(["Docker"]))
    assert signal == 0.0
    assert canonical is None


def test_java_and_javascript_do_not_match():
    signal, _ = canonical_signal(["Java"], _evidence(["JavaScript"]))
    assert signal == 0.0


def test_react_and_react_native_do_not_match():
    signal, _ = canonical_signal(["React"], _evidence(["React Native"]))
    assert signal == 0.0


def test_no_requirement_technologies_is_not_applicable():
    signal, canonical = canonical_signal([], _evidence(["Python"]))
    assert signal is None
    assert canonical is None


# --- guardrail (spec §6, §16) ---

def test_known_mismatch_is_detected():
    assert is_known_technology_mismatch(["Kubernetes"], _evidence(["Docker"])) is True


def test_no_evidence_technology_is_not_a_mismatch():
    """Absence of evidence is not the same as contradicting evidence."""
    assert is_known_technology_mismatch(["Kubernetes"], _evidence([])) is False


def test_matching_technology_is_not_a_mismatch():
    assert is_known_technology_mismatch(["PostgreSQL"], _evidence(["Postgres"])) is False
