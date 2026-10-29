from functools import lru_cache
from typing import Protocol

from fastembed import TextEmbedding

from app.config import settings


class Embedder(Protocol):
    """Anything that can turn texts into vectors."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class FastEmbedEmbedder:
    """Local embeddings using fastembed (ONNX). The model is loaded on first use."""

    def __init__(self, model_name: str, cache_dir: str | None = None):
        self._model_name = model_name
        self._cache_dir = cache_dir
        self._model: TextEmbedding | None = None

    def _get_model(self) -> TextEmbedding:
        if self._model is None:
            self._model = TextEmbedding(
                model_name=self._model_name,
                cache_dir=self._cache_dir,
            )
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vector.tolist() for vector in self._get_model().embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embedder() -> Embedder:
    return FastEmbedEmbedder(settings.embedding_model, settings.embedding_cache_dir)