from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

class PdfExtractionError(Exception):
    """Raised when a PDF cannot be read or has no extractable text."""

def extract_text(file_path: Path) -> str:
    path = Path(file_path)

    if not path.is_file():
        raise PdfExtractionError(f"File not found: {file_path}")

    try:
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
    except PdfReadError as exc:
        raise PdfExtractionError(f"Invalid or corrupted PDF: {file_path}") from exc

    text = "\n".join(pages).strip()

    if not text:
        raise PdfExtractionError(f"No extractable text in {file_path} (scanned PDFs need OCR)")

    return text