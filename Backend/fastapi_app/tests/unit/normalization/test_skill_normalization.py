from app.modules.normalization.entities import normalize_skill
from app.modules.normalization.schemas import EntityType, NormalizationMethod, NormalizationStatus


def test_exact_match():
    r = normalize_skill("Python")
    assert r.canonical_value == "Python"
    assert r.normalization_method == NormalizationMethod.EXACT
    assert r.normalization_status == NormalizationStatus.RESOLVED
    assert r.confidence == 1.0


def test_case_normalization():
    r = normalize_skill("python")
    assert r.canonical_value == "Python"
    assert r.normalization_method == NormalizationMethod.CASE_NORMALIZATION


def test_alias_postgres():
    r = normalize_skill("Postgres")
    assert r.canonical_value == "PostgreSQL"
    assert r.entity_type == EntityType.DATABASE
    assert r.normalization_method == NormalizationMethod.ALIAS


def test_alias_reactjs():
    r = normalize_skill("React.js")
    assert r.canonical_value == "React"
    assert r.normalization_method == NormalizationMethod.ALIAS


def test_alias_nodejs():
    r = normalize_skill("NodeJS")
    assert r.canonical_value == "Node.js"


def test_formatting_normalization_scikit_learn():
    r = normalize_skill("scikit learn")
    assert r.canonical_value == "scikit-learn"
    assert r.normalization_method == NormalizationMethod.FORMATTING_NORMALIZATION


def test_alias_sklearn():
    r = normalize_skill("sklearn")
    assert r.canonical_value == "scikit-learn"
    assert r.normalization_method == NormalizationMethod.ALIAS


def test_alias_java_script():
    r = normalize_skill("Java Script")
    assert r.canonical_value == "JavaScript"


def test_alias_c_plus_plus():
    r = normalize_skill("C plus plus")
    assert r.canonical_value == "C++"


def test_alias_python3_and_python3x():
    assert normalize_skill("Python3").canonical_value == "Python"
    assert normalize_skill("Python 3.x").canonical_value == "Python"


# --- Distinct entities must NOT be merged (spec §4) ---

def test_docker_and_kubernetes_are_distinct():
    assert normalize_skill("Docker").canonical_value != normalize_skill("Kubernetes").canonical_value


def test_aws_azure_gcp_are_distinct():
    canonicals = {normalize_skill(c).canonical_value for c in ("AWS", "Azure", "GCP")}
    assert canonicals == {"AWS", "Azure", "GCP"}


def test_java_and_javascript_are_distinct():
    assert normalize_skill("Java").canonical_value == "Java"
    assert normalize_skill("JavaScript").canonical_value == "JavaScript"


def test_react_and_react_native_are_distinct():
    assert normalize_skill("React").canonical_value == "React"
    assert normalize_skill("React Native").canonical_value == "React Native"


def test_postgresql_and_mysql_are_distinct():
    assert normalize_skill("PostgreSQL").canonical_value != normalize_skill("MySQL").canonical_value


def test_python_and_django_have_different_entity_types():
    """spec §4: related technologies at different layers must not collapse."""
    python = normalize_skill("Python")
    django = normalize_skill("Django")
    assert python.entity_type == EntityType.PROGRAMMING_LANGUAGE
    assert django.entity_type == EntityType.FRAMEWORK
    assert python.canonical_value != django.canonical_value


def test_c_c_plus_plus_c_sharp_do_not_collide():
    """Regression: stripping '+'/'#' during formatting normalization
    would otherwise collapse C, C++, and C# onto the same key."""
    c = normalize_skill("C").canonical_value
    cpp = normalize_skill("C++").canonical_value
    csharp = normalize_skill("C#").canonical_value
    assert len({c, cpp, csharp}) == 3


# --- Ambiguity (spec §20) ---

def test_ambiguous_term_returns_unknown_canonical():
    r = normalize_skill("Spring")
    assert r.canonical_value is None
    assert r.normalization_status == NormalizationStatus.AMBIGUOUS


def test_spring_boot_is_not_ambiguous():
    """Only the bare ambiguous term is flagged — a qualified, unambiguous
    variant resolves normally."""
    r = normalize_skill("Spring Boot")
    assert r.canonical_value == "Spring Boot"
    assert r.normalization_status == NormalizationStatus.RESOLVED


# --- Unknown (spec §8, §26: prefer Unknown over incorrect) ---

def test_unrecognized_term_is_unknown_not_guessed():
    r = normalize_skill("SomeObscureInternalToolXYZ")
    assert r.canonical_value is None
    assert r.normalization_status == NormalizationStatus.UNKNOWN
    assert r.normalization_method == NormalizationMethod.UNKNOWN
    assert r.confidence == 0.0


def test_related_but_distinct_concepts_are_not_silently_equated():
    """spec §14: 'Relational Database'/'SQL Database' must not collapse
    into 'SQL' just because they're related."""
    assert normalize_skill("Relational Database").canonical_value is None
    assert normalize_skill("SQL Database").canonical_value is None
    assert normalize_skill("SQL").canonical_value == "SQL"


# --- Determinism (spec §21) ---

def test_normalization_is_deterministic():
    results = [normalize_skill("Postgres") for _ in range(5)]
    assert len({r.canonical_value for r in results}) == 1
    assert all(r.confidence == 1.0 for r in results)


def test_knowledge_version_is_present():
    r = normalize_skill("Python")
    assert r.knowledge_version == "KNOWLEDGE_V1"


def test_raw_value_and_normalized_text_are_preserved():
    r = normalize_skill("  Postgres  ")
    assert r.raw_value == "  Postgres  "
    assert r.normalized_text == "postgres"
