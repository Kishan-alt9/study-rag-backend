"""Split PDF page text into overlapping chunks with source-page metadata."""

import re
from collections.abc import Sequence
from typing import TypedDict

from study_rag.pdf_reader import PDFPage


class TextChunk(TypedDict):
    """A text chunk and the source pages that contribute non-whitespace text."""

    source: str
    pages: list[int]
    chunk_index: int
    text: str


_PARAGRAPH_BOUNDARY = re.compile(r"\n[ \t]*\n+")
_SENTENCE_BOUNDARY = re.compile(r"""[.!?]["')\]]*\s+""")
_WHITESPACE_BOUNDARY = re.compile(r"\s+")


def _choose_chunk_end(text: str, start: int, chunk_size: int, overlap: int) -> int:
    """Choose a preferred boundary without making the next chunk stall."""
    limit = min(start + chunk_size, len(text))
    if limit == len(text):
        return limit

    minimum_end = start + overlap + 1
    preferred_minimum = max(minimum_end, start + chunk_size // 2)

    for boundary_pattern in (
        _PARAGRAPH_BOUNDARY,
        _SENTENCE_BOUNDARY,
        _WHITESPACE_BOUNDARY,
    ):
        ends = [
            match.end()
            for match in boundary_pattern.finditer(text, start, limit)
            if preferred_minimum <= match.end() <= limit
        ]
        if ends:
            return ends[-1]

    whitespace_ends = [
        match.end()
        for match in _WHITESPACE_BOUNDARY.finditer(text, start, limit)
        if minimum_end <= match.end() <= limit
    ]
    if whitespace_ends:
        return whitespace_ends[-1]

    return limit


def _build_source_text(
    pages: Sequence[PDFPage],
) -> tuple[str, list[tuple[int, int, int]]]:
    """Join non-empty page text and retain source ranges for page attribution."""
    pieces: list[str] = []
    page_ranges: list[tuple[int, int, int]] = []
    current_length = 0

    for page in pages:
        page_text = page["text"]
        if page_text == "":
            continue
        if pieces:
            separator = "\n\n"
            pieces.append(separator)
            current_length += len(separator)

        start = current_length
        pieces.append(page_text)
        current_length += len(page_text)
        page_ranges.append((start, current_length, page["page"]))

    return "".join(pieces), page_ranges


def _chunk_source(
    source: str,
    pages: Sequence[PDFPage],
    chunk_size: int,
    overlap: int,
) -> list[TextChunk]:
    text, page_ranges = _build_source_text(pages)
    chunks: list[TextChunk] = []
    start = 0

    while start < len(text):
        end = _choose_chunk_end(text, start, chunk_size, overlap)
        chunk_text = text[start:end]
        if any(not character.isspace() for character in chunk_text):
            contributing_pages: list[int] = []
            for page_start, page_end, page_number in page_ranges:
                intersection_start = max(start, page_start)
                intersection_end = min(end, page_end)
                if intersection_start < intersection_end and any(
                    not character.isspace()
                    for character in text[intersection_start:intersection_end]
                ):
                    if page_number not in contributing_pages:
                        contributing_pages.append(page_number)

            chunks.append(
                {
                    "source": source,
                    "pages": contributing_pages,
                    "chunk_index": len(chunks),
                    "text": chunk_text,
                }
            )

        if end == len(text):
            break
        start = end - overlap

    return chunks


def chunk_pages(
    pages: Sequence[PDFPage],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:
    """Convert ordered PDF page records into overlapping text chunks.

    Consecutive records with the same source are combined, with ``"\\n\\n"``
    inserted between non-empty page text fields. Empty text fields add no
    separator; whitespace-only text is retained but does not count as a page
    contribution. Chunk boundaries are preferred at paragraphs, sentences,
    and whitespace, in that order, with a hard character split as a fallback.
    Overlap is measured in Python characters.

    A source appearing again after a different source starts a new independent
    run. Runs are emitted in input order and each run starts its chunk index at
    zero; source runs are never merged across an intervening record.

    Args:
        pages: Page records in document/input order, as returned by the PDF reader.
        chunk_size: Maximum number of characters in a chunk; must be positive.
        overlap: Number of characters repeated between consecutive chunk windows;
            must be non-negative and smaller than ``chunk_size``.

    Raises:
        ValueError: If ``chunk_size`` or ``overlap`` is not an integer in range.
    """
    if (
        isinstance(chunk_size, bool)
        or not isinstance(chunk_size, int)
        or chunk_size <= 0
    ):
        raise ValueError("chunk_size must be a positive integer")
    if isinstance(overlap, bool) or not isinstance(overlap, int) or overlap < 0:
        raise ValueError("overlap must be a non-negative integer")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    run: list[PDFPage] = []

    for page in pages:
        source = page["source"]
        if run and source != run[0]["source"]:
            chunks.extend(_chunk_source(run[0]["source"], run, chunk_size, overlap))
            run = []
        run.append(page)

    if run:
        chunks.extend(_chunk_source(run[0]["source"], run, chunk_size, overlap))

    return chunks
