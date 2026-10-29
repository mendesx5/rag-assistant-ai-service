import numpy as np

from app.rag import embeddings
from app.rag.embeddings import FastEmbedEmbedder


class FakeTextEmbedding:
    """Stands in for fastembed's TextEmbedding so tests never download a model."""

    instances = 0

    def __init__(self, model_name, cache_dir=None):
        FakeTextEmbedding.instances += 1

    def embed(self, texts):
        for text in texts:
            yield np.array([float(len(text)), 1.0, 0.0])


def make_embedder(monkeypatch) -> FastEmbedEmbedder:
    FakeTextEmbedding.instances = 0
    monkeypatch.setattr(embeddings, "TextEmbedding", FakeTextEmbedding)
    return FastEmbedEmbedder("any-model")


def test_embed_documents_returns_one_vector_of_floats_per_text(monkeypatch):
    embedder = make_embedder(monkeypatch)

    vectors = embedder.embed_documents(["abc", "hello world"])

    assert vectors == [[3.0, 1.0, 0.0], [11.0, 1.0, 0.0]]
    assert isinstance(vectors[0], list)


def test_embed_query_returns_a_single_vector(monkeypatch):
    embedder = make_embedder(monkeypatch)

    assert embedder.embed_query("abc") == [3.0, 1.0, 0.0]


def test_model_is_loaded_lazily_and_only_once(monkeypatch):
    embedder = make_embedder(monkeypatch)
    assert FakeTextEmbedding.instances == 0

    embedder.embed_documents(["a"])
    embedder.embed_documents(["b"])

    assert FakeTextEmbedding.instances == 1


def test_embed_documents_with_empty_list_does_not_load_the_model(monkeypatch):
    embedder = make_embedder(monkeypatch)

    assert embedder.embed_documents([]) == []
    assert FakeTextEmbedding.instances == 0