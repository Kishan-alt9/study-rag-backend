import unittest

from study_rag.chunker import chunk_pages
from study_rag.pdf_reader import PDFPage


def page(source: str, page_number: int, text: str) -> PDFPage:
    return {"source": source, "page": page_number, "text": text}


class ChunkPagesTests(unittest.TestCase):
    def test_default_chunk_size_and_overlap(self) -> None:
        chunks = chunk_pages([page("notes.pdf", 1, "x" * 1200)])

        self.assertEqual(len(chunks[0]["text"]), 1000)
        self.assertEqual(chunks[0]["text"][-150:], chunks[1]["text"][:150])

    def test_short_text_fits_in_one_chunk(self) -> None:
        chunks = chunk_pages([page("notes.pdf", 1, "Short study notes.")])

        self.assertEqual(
            chunks,
            [
                {
                    "source": "notes.pdf",
                    "pages": [1],
                    "chunk_index": 0,
                    "text": "Short study notes.",
                }
            ],
        )

    def test_long_text_is_split_within_character_limit(self) -> None:
        chunks = chunk_pages([page("notes.pdf", 1, "abcdefghij" * 4)], 12, 2)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk["text"]) <= 12 for chunk in chunks))
        self.assertEqual([chunk["chunk_index"] for chunk in chunks], list(range(len(chunks))))

    def test_adjacent_chunks_have_configured_overlap(self) -> None:
        chunks = chunk_pages([page("notes.pdf", 1, "abcdefghijklmnopqrstuvwxyz")], 10, 3)

        for previous, current in zip(chunks, chunks[1:]):
            self.assertEqual(previous["text"][-3:], current["text"][:3])

    def test_meaningful_text_is_preserved_across_overlapping_chunks(self) -> None:
        text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"

        chunks = chunk_pages([page("notes.pdf", 1, text)], chunk_size=24, overlap=6)
        reconstructed = chunks[0]["text"] + "".join(
            chunk["text"][6:] for chunk in chunks[1:]
        )

        self.assertGreater(len(chunks), 2)
        self.assertEqual(reconstructed, text)

    def test_prefers_sentence_boundaries_where_possible(self) -> None:
        text = "First sentence. Second sentence. Third sentence."

        chunks = chunk_pages([page("notes.pdf", 1, text)], 25, 0)

        self.assertEqual(chunks[0]["text"], "First sentence. ")
        self.assertTrue(chunks[1]["text"].startswith("Second sentence. "))

    def test_unbroken_text_uses_hard_splits_and_progresses(self) -> None:
        chunks = chunk_pages([page("notes.pdf", 1, "x" * 31)], 7, 2)

        self.assertEqual(
            [chunk["text"] for chunk in chunks],
            ["x" * 7, "x" * 7, "x" * 7, "x" * 7, "x" * 7, "x" * 6],
        )
        self.assertTrue(all(0 < len(chunk["text"]) <= 7 for chunk in chunks))

    def test_chunks_text_across_pages_with_source_metadata(self) -> None:
        chunks = chunk_pages(
            [
                page("lessons.pdf", 1, "First page content."),
                page("lessons.pdf", 2, "Second page content."),
                page("lessons.pdf", 3, "Third page content."),
            ],
            chunk_size=100,
            overlap=10,
        )

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["source"], "lessons.pdf")
        self.assertEqual(chunks[0]["pages"], [1, 2, 3])
        self.assertEqual(
            chunks[0]["text"],
            "First page content.\n\nSecond page content.\n\nThird page content.",
        )

    def test_pdf_sources_are_never_combined(self) -> None:
        chunks = chunk_pages(
            [page("a.pdf", 1, "Alpha"), page("b.pdf", 1, "Bravo")],
            chunk_size=100,
            overlap=10,
        )

        self.assertEqual(
            [(chunk["source"], chunk["pages"], chunk["chunk_index"]) for chunk in chunks],
            [("a.pdf", [1], 0), ("b.pdf", [1], 0)],
        )
        self.assertEqual([chunk["text"] for chunk in chunks], ["Alpha", "Bravo"])

    def test_empty_and_whitespace_only_pages_emit_no_empty_chunks(self) -> None:
        chunks = chunk_pages(
            [
                page("notes.pdf", 1, ""),
                page("notes.pdf", 2, " \n\t "),
                page("notes.pdf", 3, "Actual notes."),
                page("notes.pdf", 4, "  "),
            ],
            chunk_size=100,
            overlap=10,
        )

        self.assertEqual(len(chunks), 1)
        self.assertTrue(chunks[0]["text"].strip())
        self.assertEqual(chunks[0]["pages"], [3])

    def test_empty_input_returns_no_chunks(self) -> None:
        self.assertEqual(chunk_pages([]), [])

    def test_invalid_chunk_sizes_raise_clear_value_errors(self) -> None:
        for chunk_size in (0, -1, 1.5, True):
            with self.subTest(chunk_size=chunk_size):
                with self.assertRaisesRegex(ValueError, "chunk_size must be a positive integer"):
                    chunk_pages([], chunk_size=chunk_size)  # type: ignore[arg-type]

    def test_invalid_overlaps_raise_clear_value_errors(self) -> None:
        for overlap, message in (
            (-1, "overlap must be a non-negative integer"),
            (1.5, "overlap must be a non-negative integer"),
            (True, "overlap must be a non-negative integer"),
            (10, "overlap must be smaller than chunk_size"),
        ):
            with self.subTest(overlap=overlap):
                with self.assertRaisesRegex(ValueError, message):
                    chunk_pages([], chunk_size=10, overlap=overlap)  # type: ignore[arg-type]

    def test_every_chunk_is_non_empty_and_within_limit(self) -> None:
        chunks = chunk_pages(
            [page("notes.pdf", 1, "A paragraph. " * 20)],
            chunk_size=20,
            overlap=4,
        )

        self.assertTrue(chunks)
        for chunk in chunks:
            self.assertTrue(chunk["text"].strip())
            self.assertLessEqual(len(chunk["text"]), 20)

    def test_identical_input_and_configuration_are_deterministic(self) -> None:
        input_pages = [
            page("notes.pdf", 1, "First paragraph.\n\n"),
            page("notes.pdf", 2, "Second paragraph with more detail."),
        ]

        self.assertEqual(
            chunk_pages(input_pages, chunk_size=18, overlap=5),
            chunk_pages(input_pages, chunk_size=18, overlap=5),
        )

    def test_pages_only_contribute_when_their_non_whitespace_text_is_in_chunk(self) -> None:
        chunks = chunk_pages(
            [
                page("notes.pdf", 1, "aaaa"),
                page("notes.pdf", 2, ""),
                page("notes.pdf", 3, "bbbb"),
            ],
            chunk_size=5,
            overlap=1,
        )

        self.assertEqual(chunks[0]["text"], "aaaa\n")
        self.assertEqual(chunks[0]["pages"], [1])
        self.assertTrue(all(2 not in chunk["pages"] for chunk in chunks))
        self.assertEqual(chunks[-1]["pages"], [3])

    def test_non_consecutive_source_runs_are_not_merged(self) -> None:
        chunks = chunk_pages(
            [
                page("a.pdf", 1, "First appearance."),
                page("b.pdf", 1, "Other document."),
                page("a.pdf", 2, "Second appearance."),
            ],
            chunk_size=100,
            overlap=10,
        )

        self.assertEqual(
            [(chunk["source"], chunk["chunk_index"], chunk["text"]) for chunk in chunks],
            [
                ("a.pdf", 0, "First appearance."),
                ("b.pdf", 0, "Other document."),
                ("a.pdf", 0, "Second appearance."),
            ],
        )


if __name__ == "__main__":
    unittest.main()
