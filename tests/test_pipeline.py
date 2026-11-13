import pytest

from app.pdf.extractor import PdfExtractionError
from app.rag.pipeline import index_pdf


def test_index_pdf_stores_chunks_and_makes_them_searchable(make_pdf, store):
    path = make_pdf("Vacation policy: 30 days per year")

    chunk_count = index_pdf("doc-1", path, store)

    assert chunk_count == 1
    results = store.search("vacation days", "doc-1")
    assert "Vacation policy" in results[0].text


def test_index_pdf_does_not_duplicate_chunks_when_run_twice(make_pdf, store):
    path = make_pdf()

    index_pdf("doc-1", path, store)
    index_pdf("doc-1", path, store)

    assert store.count_chunks("doc-1") == 1


def test_index_pdf_raises_and_stores_nothing_when_file_is_missing(tmp_path, store):
    with pytest.raises(PdfExtractionError):
        index_pdf("doc-1", str(tmp_path / "missing.pdf"), store)

    assert store.count_chunks("doc-1") == 0