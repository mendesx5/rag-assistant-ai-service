from dataclasses import dataclass
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embeddings import Embedder, get_embedder

COLLECTION_NAME = "document_chunks"


@dataclass(frozen=True)
class SearchResult:
    text: str
    chunk_index: int
    score: float  # cosine similarity: closer to 1.0 means more similar


class VectorStore:
    def __init__(self, client: chromadb.api.ClientAPI, embedder: Embedder):
        self._collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            configuration={"hnsw": {"space": "cosine"}},
        )
        self._embedder = embedder

    def index_document(self, document_id: str, chunks: list[str]) -> int:
        """Stores the chunks of a document, replacing any previous version of it."""
        self._collection.delete(where={"document_id": document_id})
        if not chunks:
            return 0
        self._collection.add(
            ids=[f"{document_id}:{index}" for index in range(len(chunks))],
            documents=chunks,
            embeddings=self._embedder.embed_documents(chunks),
            metadatas=[
                {"document_id": document_id, "chunk_index": index}
                for index in range(len(chunks))
            ],
        )
        return len(chunks)

    def search(
        self, question: str, document_id: str, top_k: int = settings.search_top_k
    ) -> list[SearchResult]:
        """Returns the chunks of ONE document closest in meaning to the question."""
        result = self._collection.query(
            query_embeddings=[self._embedder.embed_query(question)],
            n_results=top_k,
            where={"document_id": document_id},
        )
        return [
            SearchResult(text=text, chunk_index=metadata["chunk_index"], score=1.0 - distance)
            for text, metadata, distance in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
        ]

    def count_chunks(self, document_id: str) -> int:
        return len(self._collection.get(where={"document_id": document_id}, include=[])["ids"])


@lru_cache
def get_vector_store() -> VectorStore:
    client = chromadb.PersistentClient(
        path=settings.chroma_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return VectorStore(client, get_embedder())