import logging

from app.pdf.extractor import extract_text
from app.rag.chunking import split_into_chunks
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


def index_pdf(document_id: str, file_path: str, store: VectorStore) -> int:
    """Reads a PDF, splits it into chunks and indexes them. Returns the chunk count."""
    text = extract_text(file_path)
    chunks = split_into_chunks(text)
    chunk_count = store.index_document(document_id, chunks)
    logger.info(
        "Document %s indexed: %d characters -> %d chunks", document_id, len(text), chunk_count
    )
    return chunk_count