"""Local pretrained embedding model implementation (spec §11-13).

Model choice: sentence-transformers/all-MiniLM-L6-v2 — a small (~80MB),
fast, well-established sentence-embedding model that performs well on
short technical/job-related text, runs comfortably on CPU, and needs no
GPU/training. Configurable via Settings.embedding_model_name, never
hard-coded elsewhere (spec §12).

The model is loaded lazily and once per process (import-time model
loading would slow down every test/tool that imports this package even
when it never calls embed()).
"""

import numpy as np

from app.core.config import get_settings
from app.modules.embeddings.service import EmbeddingService, Vector, cache_key

_model = None
_embedding_cache: dict[str, Vector] = {}


def _get_model():
    global _model
    if _model is None:
        # Imported lazily too — importing sentence_transformers/torch at
        # module load time would make every caller of app.modules.embeddings
        # pay that cost even if they only use NotImplementedEmbeddingService.
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(get_settings().embedding_model_name)
    return _model


class LocalSentenceTransformerEmbeddingService(EmbeddingService):
    def __init__(self):
        self.model_version = get_settings().embedding_model_name

    def embed(self, text: str) -> Vector:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[Vector]:
        """Cache-aware: only texts not already in the process-local cache
        are actually sent to the model, and only once per unique text
        (spec §26 — "avoid repeatedly embedding identical text").
        """
        results: list[Vector | None] = [None] * len(texts)
        to_embed: list[str] = []
        to_embed_indices: list[int] = []

        for i, text in enumerate(texts):
            key = cache_key(text, self.model_version)
            cached = _embedding_cache.get(key)
            if cached is not None:
                results[i] = cached
            else:
                to_embed.append(text)
                to_embed_indices.append(i)

        if to_embed:
            model = _get_model()
            vectors = model.encode(to_embed, convert_to_numpy=True, show_progress_bar=False)
            for idx, text, vector in zip(to_embed_indices, to_embed, vectors):
                vector_list = [float(v) for v in vector]
                results[idx] = vector_list
                _embedding_cache[cache_key(text, self.model_version)] = vector_list

        return results  # type: ignore[return-value]

    def similarity(self, a: Vector, b: Vector) -> float:
        """Cosine similarity, clamped to [0, 1] — raw embedding cosine
        similarity for normalized sentence embeddings is already close to
        [-1, 1] and in practice rarely goes negative for this model, but
        the clamp keeps the contract exact regardless.
        """
        vec_a, vec_b = np.array(a), np.array(b)
        denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
        if denom == 0:
            return 0.0
        cosine = float(np.dot(vec_a, vec_b) / denom)
        return max(0.0, min(1.0, cosine))
