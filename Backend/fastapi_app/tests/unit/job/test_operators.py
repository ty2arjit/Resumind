from app.modules.job.operators import detect_operator
from app.modules.job.schemas import LogicalOperator


def test_and_operator():
    assert detect_operator("Experience with Python and FastAPI") == LogicalOperator.AND


def test_or_operator():
    assert detect_operator("Experience with AWS, Azure, or GCP") == LogicalOperator.OR


def test_single_technology_has_no_operator():
    assert detect_operator("Experience with Python") is None


def test_no_technology_has_no_operator():
    assert detect_operator("Excellent communication and teamwork") is None
