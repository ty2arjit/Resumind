from app.modules.matching.tfidf_matcher import TfidfMatcher


def test_identical_text_scores_highly():
    matcher = TfidfMatcher()
    scores = matcher.similarity("PostgreSQL database optimization", ["PostgreSQL database optimization"])
    assert scores[0] > 0.9


def test_unrelated_text_scores_low():
    matcher = TfidfMatcher()
    scores = matcher.similarity("PostgreSQL database optimization", ["unrelated marketing content about sales"])
    assert scores[0] < 0.3


def test_multiple_candidates_ranked_sensibly():
    matcher = TfidfMatcher()
    scores = matcher.similarity(
        "PostgreSQL database performance",
        ["Optimized PostgreSQL database performance significantly", "Led a marketing campaign for social media"],
    )
    assert scores[0] > scores[1]


def test_empty_evidence_list_returns_empty():
    assert TfidfMatcher().similarity("Python", []) == []


def test_does_not_raise_on_degenerate_input():
    matcher = TfidfMatcher()
    scores = matcher.similarity("", ["", "the a an"])
    assert scores == [0.0, 0.0]
