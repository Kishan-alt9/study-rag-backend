import tempfile
import unittest
from pathlib import Path

import pymupdf as fitz

from study_rag.pdf_reader import extract_pdf_pages


class ExtractPDFPagesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.temp_path = Path(self.temp_directory.name)

    def create_pdf(self, filename: str, page_texts: list[str]) -> Path:
        pdf_path = self.temp_path / filename
        with fitz.open() as document:
            for text in page_texts:
                page = document.new_page()
                if text:
                    page.insert_text((72, 72), text)
            document.save(pdf_path)
        return pdf_path

    def test_extracts_text_from_multiple_pages_in_order(self) -> None:
        pdf_path = self.create_pdf("lessons.pdf", ["First page", "Second page"])

        pages = extract_pdf_pages(pdf_path)

        self.assertEqual(len(pages), 2)
        self.assertIn("First page", pages[0]["text"])
        self.assertIn("Second page", pages[1]["text"])

    def test_records_have_source_filename_and_one_based_page_numbers(self) -> None:
        pdf_path = self.create_pdf("notes.pdf", ["Page one", "Page two"])

        pages = extract_pdf_pages(pdf_path)

        self.assertEqual(
            [(page["source"], page["page"]) for page in pages],
            [("notes.pdf", 1), ("notes.pdf", 2)],
        )

    def test_preserves_empty_page(self) -> None:
        pdf_path = self.create_pdf("with-empty-page.pdf", ["Text", "", "More text"])

        pages = extract_pdf_pages(pdf_path)

        self.assertEqual(len(pages), 3)
        self.assertEqual(pages[1]["text"], "")
        self.assertEqual(pages[1]["page"], 2)

    def test_missing_file_raises_file_not_found_error(self) -> None:
        missing_path = self.temp_path / "missing.pdf"

        with self.assertRaisesRegex(FileNotFoundError, "PDF file not found"):
            extract_pdf_pages(missing_path)

    def test_directory_raises_is_a_directory_error(self) -> None:
        with self.assertRaisesRegex(IsADirectoryError, "got a directory"):
            extract_pdf_pages(self.temp_path)

    def test_corrupt_pdf_raises_value_error(self) -> None:
        corrupt_path = self.temp_path / "corrupt.pdf"
        corrupt_path.write_bytes(b"not a PDF")

        with self.assertRaisesRegex(ValueError, "Could not read PDF file"):
            extract_pdf_pages(corrupt_path)

    def test_encrypted_pdf_raises_permission_error(self) -> None:
        encrypted_path = self.temp_path / "encrypted.pdf"
        with fitz.open() as document:
            document.new_page()
            document.save(
                encrypted_path,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw="owner-password",
                user_pw="user-password",
            )

        with self.assertRaisesRegex(PermissionError, "encrypted"):
            extract_pdf_pages(encrypted_path)


if __name__ == "__main__":
    unittest.main()
