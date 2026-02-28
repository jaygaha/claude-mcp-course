"""
Intelligent text chunking with sentence-boundary awareness.

Splits long documents into overlapping pieces that respect natural
sentence boundaries, preventing mid-sentence or mid-word breaks.
The overlap ensures context isn't lost between adjacent chunks.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """
    A numbered slice of a document.

    Attributes:
        index:      Zero-based position in the sequence.
        text:       The chunk content.
        char_count: Number of characters in this chunk.
    """
    index: int
    text: str
    char_count: int

    @property
    def preview(self) -> str:
        """First 80 characters for logging / display."""
        return self.text[:80].replace("\n", " ") + ("…" if len(self.text) > 80 else "")


class TextChunker:
    """
    Splits text into overlapping, sentence-aware chunks.

    Algorithm:
      1. If the full text fits in one chunk, return it as-is.
      2. Otherwise, advance a sliding window of `chunk_size` chars.
      3. At each step, look backwards from the window edge for a
         sentence-ending punctuation mark followed by whitespace.
      4. Slide forward by (chunk_end − overlap) to start the next chunk.

    Args:
        chunk_size: Maximum characters per chunk (default 4000).
        overlap:    Characters of overlap between chunks (default 200).
    """

    def __init__(self, chunk_size: int = 4000, overlap: int = 200) -> None:
        if overlap >= chunk_size:
            raise ValueError(
                f"overlap ({overlap}) must be strictly less than "
                f"chunk_size ({chunk_size})."
            )
        self._size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str) -> list[Chunk]:
        """
        Split `text` into a list of Chunk objects.

        Short texts (≤ chunk_size) are returned as a single chunk.
        """
        # Fast path: fits in one chunk
        if len(text) <= self._size:
            return [Chunk(index=0, text=text, char_count=len(text))]

        chunks: list[Chunk] = []
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + self._size, len(text))

            # Try to snap to a sentence boundary
            if end < len(text):
                boundary = self._find_sentence_boundary(text, start, end)
                if boundary > start:
                    end = boundary

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    index=idx,
                    text=chunk_text,
                    char_count=len(chunk_text),
                ))
                idx += 1

            # Advance with overlap
            start = max(start + 1, end - self._overlap)

        logger.info(
            "Chunked %d chars → %d chunks (size=%d, overlap=%d)",
            len(text), len(chunks), self._size, self._overlap,
        )
        return chunks

    # ── Internal ────────────────────────────────────────────────────────

    @staticmethod
    def _find_sentence_boundary(text: str, start: int, end: int) -> int:
        """
        Scan backwards from `end` within [start, end) for the last
        sentence-ending punctuation (.!?) followed by whitespace.

        Returns the character position just after the whitespace,
        or `end` if no boundary is found.
        """
        search_zone = text[start:end]
        matches = list(re.finditer(r'[.!?]\s', search_zone))
        if matches:
            # Return absolute position after the matched whitespace
            return start + matches[-1].end()
        return end