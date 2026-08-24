"""Offline schema checks — no database connection required. Confirms every
entity from the Master Specification's core entity list is registered on
Base.metadata, and that Prisma's snake_case @@map naming was mirrored
correctly on the SQLAlchemy side.
"""

from app.models import Base

EXPECTED_TABLES = {
    "users",
    "resumes",
    "resume_versions",
    "job_descriptions",
    "target_profiles",
    "analyses",
    "requirements",
    "requirement_matches",
    "evidence",
    "recommendations",
    "score_breakdowns",
    "evaluation_cases",
    "evaluation_results",
}


def test_all_spec_entities_are_registered():
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))


def test_analysis_table_has_versioning_columns():
    columns = {c.name for c in Base.metadata.tables["analyses"].columns}
    assert {"algorithm_version", "scoring_config_version", "embedding_model_version"}.issubset(columns)
