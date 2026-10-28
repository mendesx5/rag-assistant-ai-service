import pytest

from app.pdf.extractor import PdfExtractionError, extract_text


def test_extract_text_returns_pdf_content(make_pdf):
    path = make_pdf("Vacation policy: 30 days per year")

    assert "Vacation policy" in extract_text(path)


def test_extract_text_raises_when_file_does_not_exist(tmp_path):
    with pytest.raises(PdfExtractionError):
        extract_text(str(tmp_path / "missing.pdf"))


def test_extract_text_raises_for_corrupted_pdf(tmp_path):
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"this is not a pdf")

    with pytest.raises(PdfExtractionError):
        extract_text(str(broken))