from app.modules.evidence.dedup import deduplicate
from app.modules.evidence.schemas import EvidenceItem, EvidenceSourceType


def _item(id, text):
    return EvidenceItem(id=id, text=text, section=EvidenceSourceType.EXPERIENCE_BULLET, source_type="BULLET")


def test_exact_duplicate_is_removed():
    items = [_item("ev_1", "Built REST APIs using FastAPI."), _item("ev_2", "Built REST APIs using FastAPI.")]
    result, warnings = deduplicate(items)
    assert len(result) == 1
    assert len(warnings) == 1


def test_near_duplicate_differing_only_by_case_and_punctuation_is_removed():
    items = [_item("ev_1", "Built REST APIs using FastAPI."), _item("ev_2", "built rest apis using fastapi")]
    result, _ = deduplicate(items)
    assert len(result) == 1


def test_distinct_evidence_is_preserved():
    items = [_item("ev_1", "Built REST APIs."), _item("ev_2", "Optimized database queries.")]
    result, warnings = deduplicate(items)
    assert len(result) == 2
    assert warnings == []


def test_first_occurrence_is_kept():
    items = [_item("ev_1", "Python"), _item("ev_2", "Python")]
    result, _ = deduplicate(items)
    assert result[0].id == "ev_1"
