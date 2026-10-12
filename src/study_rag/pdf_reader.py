"""Read text from PDF pages without modifying the source document."""

from pathlib import Path
from typing import TypedDict

import pymupdf as fitz


class PDFPage(TypedDict):
    """Text and source information for one PDF page."""

    source: str
    page: int
    text: str


def extract_pdf_pages(pdf_path: str | Path) -> list[PDFPage]:
    """Return one text record per page in a PDF, including empty pages.

    Raises:
        FileNotFoundError: If ``pdf_path`` does not exist.
        IsADirectoryError: If ``pdf_path`` names a directory.
        ValueError: If the path is not a regular file or PyMuPDF cannot read it.
        PermissionError: If a password is required or access is denied.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a PDF file, got a directory: {path}")
    if not path.is_file():
        raise ValueError(f"Expected a regular PDF file: {path}")

    try:
        with fitz.open(str(path)) as document:
            if document.needs_pass:
                raise PermissionError(
                    f"PDF is encrypted and requires a password: {path}"
                )

            return [
                {
                    "source": path.name,
                    "page": page_number,
                    "text": page.get_text(),
                }
                for page_number, page in enumerate(document, start=1)
            ]
    except fitz.FileDataError as error:
        raise ValueError(f"Could not read PDF file '{path}': {error}") from error
