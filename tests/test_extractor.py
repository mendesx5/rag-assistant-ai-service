import pytest

from app.pdf.extractor import PdfExtractionError, extract_text


def build_pdf(text: str) -> bytes:
    """Builds a minimal one-page PDF containing the given text."""
    stream = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
        + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_position = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for offset in offsets:
        pdf += f"{offset:010d} 00000 n \n".encode()
    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF\n"
    ).encode()
    return pdf


def test_extract_text_returns_pdf_content(tmp_path):
    pdf_file = tmp_path / "manual.pdf"
    pdf_file.write_bytes(build_pdf("Vacation policy: 30 days per year"))

    text = extract_text(str(pdf_file))

    assert "Vacation policy" in text


def test_extract_text_raises_when_file_does_not_exist(tmp_path):
    with pytest.raises(PdfExtractionError):
        extract_text(str(tmp_path / "missing.pdf"))


def test_extract_text_raises_for_corrupted_pdf(tmp_path):
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"this is not a pdf")

    with pytest.raises(PdfExtractionError):
        extract_text(str(broken))