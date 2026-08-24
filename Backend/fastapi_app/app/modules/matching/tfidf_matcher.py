"""TF-IDF matching (spec §9-10).

Encapsulated behind TfidfMatcher with a clean API — never a global
vectorizer fit over an entire resume/JD corpus. Each call fits a fresh
vectorizer over a small local corpus (one requirement + its candidate
evidence texts only), matching the spec's explicit scope: requirement
vs. relevant evidence, not whole-document vs. whole-document.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfMatcher:
    def similarity(self, requirement_text: str, evidence_texts: list[str]) -> list[float]:
        """Returns one cosine-similarity score per evidence text, in the
        same order as `evidence_texts`. Never raises on degenerate input
        (all-stopword text, empty strings) — returns zeros instead."""
        if not evidence_texts:
            return []

        corpus = [requirement_text] + evidence_texts
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform(corpus)
        except ValueError:
            return [0.0] * len(evidence_texts)

        if matrix.shape[1] == 0:
            return [0.0] * len(evidence_texts)

        requirement_vector = matrix[0:1]
        evidence_vectors = matrix[1:]
        similarities = cosine_similarity(requirement_vector, evidence_vectors)[0]
        return [max(0.0, min(1.0, float(s))) for s in similarities]
