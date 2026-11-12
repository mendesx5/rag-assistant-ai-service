import chromadb
import pytest

from app.rag.vector_store import VectorStore

VOCABULARY = ["vacation", "days", "expense", "reimbursement", "parking", "basement"]


class FakeEmbedder:
    """Counts known words, so texts sharing words end up close to each other."""

    def _vector(self, text: str) -> list[float]:
        words = text.lower().split()
        return [float(words.count(word)) for word in VOCABULARY] + [0.01]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


CHUNKS = [
    "employees get thirty vacation days per year",
    "travel expense reimbursement happens within ten days",
    "parking is located in the basement",
]


@pytest.fixture
def store(tmp_path) -> VectorStore:
    return VectorStore(chromadb.PersistentClient(path=str(tmp_path)), FakeEmbedder())


def test_index_document_returns_the_number_of_chunks(store):
    assert store.index_document("doc-1", CHUNKS) == 3
    assert store.count_chunks("doc-1") == 3


def test_search_returns_the_most_similar_chunk_first(store):
    store.index_document("doc-1", CHUNKS)

    results = store.search("vacation days", "doc-1", top_k=3)

    assert results[0].text == CHUNKS[0]
    assert results[0].chunk_index == 0
    assert results[0].score > results[1].score


def test_search_only_returns_chunks_of_the_requested_document(store):
    store.index_document("doc-1", CHUNKS)
    store.index_document("doc-2", ["vacation days are unlimited here"])

    results = store.search("vacation days", "doc-2", top_k=5)

    assert [result.text for result in results] == ["vacation days are unlimited here"]


def test_indexing_the_same_document_twice_does_not_duplicate_chunks(store):
    store.index_document("doc-1", CHUNKS)
    store.index_document("doc-1", CHUNKS)

    assert store.count_chunks("doc-1") == 3


def test_reindexing_with_fewer_chunks_removes_the_old_ones(store):
    store.index_document("doc-1", CHUNKS)
    store.index_document("doc-1", CHUNKS[:1])

    assert store.count_chunks("doc-1") == 1


def test_indexing_no_chunks_stores_nothing(store):
    assert store.index_document("doc-1", []) == 0
    assert store.count_chunks("doc-1") == 0


def test_search_on_unknown_document_returns_empty_list(store):
    assert store.search("vacation days", "missing-doc") == []