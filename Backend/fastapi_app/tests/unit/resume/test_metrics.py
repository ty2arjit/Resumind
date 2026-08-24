from app.modules.resume.metrics import extract_metrics


def test_percentage():
    assert "35%" in extract_metrics("reduced latency by 35%")


def test_multiplier():
    assert "3x" in extract_metrics("improved throughput by 3x")


def test_count_with_k_suffix():
    metrics = extract_metrics("scaled to support 10K users")
    assert any("10K" in m for m in metrics)


def test_plus_count():
    metrics = extract_metrics("led 50+ projects")
    assert any("50+" in m for m in metrics)


def test_time_duration():
    assert any("2 seconds" in m for m in extract_metrics("cut load time to 2 seconds"))
    assert any("40 hours" in m for m in extract_metrics("saved 40 hours per week"))


def test_currency():
    metrics = extract_metrics("raised ₹5 lakh in funding")
    assert any("₹5" in m for m in metrics)


def test_no_metric_present():
    assert extract_metrics("Collaborated with the design team") == []


def test_preserves_original_representation_not_judgment():
    metrics = extract_metrics("35%")
    assert metrics == ["35%"]
