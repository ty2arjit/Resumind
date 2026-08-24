from app.modules.resume.evidence import build_evidence
from app.modules.resume.schemas import CanonicalSection


def test_spec_example_bullet():
    """The exact example from RESUMIND_ATS_MASTER_SPECIFICATION.md §11."""
    text = "Built REST APIs using FastAPI and PostgreSQL, reducing response latency by 35%."
    ev = build_evidence(text, CanonicalSection.EXPERIENCE)

    assert ev.text == text
    assert ev.section == CanonicalSection.EXPERIENCE
    assert "Built" in ev.actions
    assert "FastAPI" in ev.technologies
    assert "PostgreSQL" in ev.technologies
    assert "35%" in ev.metrics
    assert "response latency" in ev.objects


def test_evidence_carries_position_context():
    ev = build_evidence("Wrote unit tests.", CanonicalSection.EXPERIENCE, position="Backend Intern")
    assert ev.position == "Backend Intern"


def test_bullet_with_no_action_no_technology_no_metric():
    ev = build_evidence("Worked closely with stakeholders.", CanonicalSection.EXPERIENCE)
    assert ev.actions == []
    assert ev.technologies == []
    assert ev.metrics == []


def test_evidence_does_not_judge_or_score():
    """Spec §20/§11: evidence extraction must not decide whether the bullet
    satisfies anything — the Evidence schema has no score/match field."""
    ev = build_evidence("Built something.", CanonicalSection.EXPERIENCE)
    assert not hasattr(ev, "score")
    assert not hasattr(ev, "matched")
