from app.models.enums import MatchStrength
from app.modules.matching.fusion import classify_match_strength, fuse_signals
from app.modules.matching.schemas import MatchSignals


def test_perfect_signals_fuse_near_one():
    signals = MatchSignals(exact=1.0, canonical=1.0, keyword=1.0, tfidf=1.0, semantic=1.0, context=1.0)
    score, confidence = fuse_signals(signals)
    assert score > 0.95
    assert confidence == 1.0


def test_all_zero_signals_fuse_to_zero():
    signals = MatchSignals(exact=0.0, canonical=0.0, keyword=0.0, tfidf=0.0, semantic=0.0, context=0.0)
    score, _ = fuse_signals(signals)
    assert score == 0.0


def test_missing_semantic_signal_is_excluded_not_zeroed():
    """Regression: a None signal must be excluded from the weighted
    average (and its weight redistributed), not silently treated as 0 —
    otherwise every non-technology requirement is structurally capped."""
    with_semantic = MatchSignals(exact=1.0, canonical=1.0, keyword=1.0, tfidf=1.0, semantic=1.0, context=1.0)
    without_semantic = MatchSignals(exact=1.0, canonical=1.0, keyword=1.0, tfidf=1.0, semantic=None, context=1.0)

    score_with, conf_with = fuse_signals(with_semantic)
    score_without, conf_without = fuse_signals(without_semantic)

    assert score_without == 1.0  # every *active* signal was perfect
    assert conf_without < conf_with  # but confidence reflects less signal coverage


def test_missing_exact_and_canonical_does_not_cap_score():
    """A responsibility requirement with no technology term at all must
    still be able to reach a high fused score from keyword/tfidf/semantic
    alone."""
    signals = MatchSignals(exact=None, canonical=None, keyword=1.0, tfidf=1.0, semantic=1.0, context=1.0)
    score, _ = fuse_signals(signals)
    assert score == 1.0


def test_classification_thresholds():
    assert classify_match_strength(1.0) == MatchStrength.VERY_STRONG
    assert classify_match_strength(0.90) == MatchStrength.STRONG
    assert classify_match_strength(0.70) == MatchStrength.PARTIAL
    assert classify_match_strength(0.40) == MatchStrength.WEAK
    assert classify_match_strength(0.0) == MatchStrength.MISSING
