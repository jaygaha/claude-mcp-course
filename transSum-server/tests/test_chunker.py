"""Tests for the text chunker."""

import pytest
from transsum.processing.chunker import TextChunker, Chunk


class TestSingleChunk:
    """Short texts should return exactly one chunk."""

    def test_short_text_returns_one_chunk(self):
        chunker = TextChunker(chunk_size=1000, overlap=100)
        chunks = chunker.chunk("Hello world.")
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world."
        assert chunks[0].index == 0

    def test_text_exactly_at_limit(self):
        chunker = TextChunker(chunk_size=10, overlap=2)
        chunks = chunker.chunk("1234567890")  # exactly 10 chars
        assert len(chunks) == 1


class TestMultipleChunks:
    """Long texts should be split into multiple overlapping chunks."""

    def test_produces_multiple_chunks(self):
        chunker = TextChunker(chunk_size=100, overlap=20)
        text = "Word " * 200  # ~1000 chars
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunks_are_within_size_limit(self):
        chunker = TextChunker(chunk_size=100, overlap=20)
        text = "This is a sentence. " * 50
        chunks = chunker.chunk(text)
        # Allow small tolerance for sentence-boundary snapping
        for c in chunks:
            assert c.char_count <= 130, f"Chunk {c.index} too large: {c.char_count}"

    def test_indices_are_sequential(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk("x " * 100)
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_no_empty_chunks(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk("word " * 80)
        assert all(c.char_count > 0 for c in chunks)
        assert all(c.text.strip() for c in chunks)


class TestSentenceBoundary:
    """Chunker should prefer to break at sentence endings."""

    def test_breaks_at_period(self):
        text = "First sentence. Second sentence. Third sentence."
        chunker = TextChunker(chunk_size=35, overlap=5)
        chunks = chunker.chunk(text)
        # First chunk should end at a sentence boundary
        assert chunks[0].text.endswith("sentence.")

    def test_handles_no_punctuation(self):
        text = "word " * 50  # no sentence endings
        chunker = TextChunker(chunk_size=30, overlap=5)
        chunks = chunker.chunk(text)
        assert len(chunks) > 1  # should still split


class TestValidation:
    """Constructor validation."""

    def test_overlap_equals_size_rejected(self):
        with pytest.raises(ValueError, match="strictly less"):
            TextChunker(chunk_size=100, overlap=100)

    def test_overlap_greater_than_size_rejected(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, overlap=150)


class TestChunkDataclass:
    """Chunk preview helper."""

    def test_preview_short_text(self):
        c = Chunk(index=0, text="Hello", char_count=5)
        assert "Hello" in c.preview

    def test_preview_long_text_truncates(self):
        c = Chunk(index=0, text="A" * 200, char_count=200)
        assert len(c.preview) < 200
        assert c.preview.endswith("…")