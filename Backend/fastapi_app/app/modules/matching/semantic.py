"""Semantic embedding matching (spec §11-14).

Only ever talks to EmbeddingService — never instantiates a model
directly. Returns None (not 0.0) when the service is unavailable, so
callers can distinguish "no semantic signal computed" from "computed and
found no similarity" (spec §23's UNKNOWN-vs-MISSING distinction applies
here too).
"""

from app.modules.embeddings import get_embedding_service
from app.modules.embeddings.service import EmbeddingServiceUnavailableError


class SemanticMatcher:
    def __init__(self):
        self._service = get_embedding_service()

    def similarity(self, requirement_text: str, evidence_texts: list[str]) -> list[float | None]:
        """One similarity score per evidence text, or all-None if the
        embedding service is unavailable."""
        if not evidence_texts:
            return []
        try:
            requirement_vector = self._service.embed(requirement_text)
            evidence_vectors = self._service.embed_batch(evidence_texts)
        except EmbeddingServiceUnavailableError:
            return [None] * len(evidence_texts)

        return [self._service.similarity(requirement_vector, vector) for vector in evidence_vectors]
