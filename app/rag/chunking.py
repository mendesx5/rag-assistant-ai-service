from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def split_into_chunks(
    text: str,
    chunk_size: int = settings.chunk_size,
    chunk_overlap: int = settings.chunk_overlap,
) -> list[str]:
    """Splits text into overlapping chunks, preferring paragraph and sentence boundaries."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)