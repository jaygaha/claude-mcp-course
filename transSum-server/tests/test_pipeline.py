"""
Tests for the processing pipeline.

Uses a mock adapter so no real LLM calls are made.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from transsum.models.base import ModelResponse
from transsum.processing.loader import DocumentLoader
from transsum.processing.chunker import TextChunker
from transsum.processing.pipeline import ProcessingPipeline, TaskType


def _mock_adapter(response_text: str = "Mock output.") -> AsyncMock:
    """Create a mock adapter that returns a fixed response."""
    adapter = AsyncMock()
    adapter.generate.return_value = ModelResponse(
        text=response_text,
        model="mock-model",
        provider="mock",
        usage={"prompt_tokens": 10, "completion_tokens": 20},
        finish_reason="stop",
    )
    adapter.close.return_value = None
    return adapter


class TestSingleChunkPipeline:
    """Short docs should go through the fast path (one LLM call)."""

    def test_summarize_short_doc(self):
        adapter = _mock_adapter("Concise summary here.")
        chunker = TextChunker(chunk_size=10000, overlap=200)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("This is a short document.")

        result = asyncio.run(pipeline.run(doc, TaskType.SUMMARIZE))

        assert result.output == "Concise summary here."
        assert result.chunks_processed == 1
        assert result.task == TaskType.SUMMARIZE
        adapter.generate.assert_called_once()

    def test_translate_short_doc(self):
        adapter = _mock_adapter("Hola mundo.")
        chunker = TextChunker(chunk_size=10000, overlap=200)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("Hello world.")

        result = asyncio.run(
            pipeline.run(doc, TaskType.TRANSLATE, language="English")
        )

        assert result.output == "Hola mundo."
        assert result.task == TaskType.TRANSLATE
        adapter.generate.assert_called_once()


class TestMultiChunkPipeline:
    """Long docs should trigger the map-reduce pattern."""

    def test_map_reduce_produces_more_calls(self):
        adapter = _mock_adapter("Partial.")
        chunker = TextChunker(chunk_size=50, overlap=10)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("Word " * 100)  # ~500 chars → multiple chunks

        result = asyncio.run(pipeline.run(doc, TaskType.SUMMARIZE))

        # At least: N chunk calls + 1 merge call
        assert adapter.generate.call_count > 2
        assert result.chunks_processed > 1

    def test_usage_tokens_accumulated(self):
        adapter = _mock_adapter("Result.")
        chunker = TextChunker(chunk_size=50, overlap=10)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("Word " * 100)

        result = asyncio.run(pipeline.run(doc, TaskType.SUMMARIZE))

        # Each call contributes 10 + 20 tokens
        total_calls = adapter.generate.call_count
        assert result.usage["prompt_tokens"] == 10 * total_calls
        assert result.usage["completion_tokens"] == 20 * total_calls


class TestPipelineMetadata:
    """Verify metadata is passed through correctly."""

    def test_model_and_provider_from_adapter(self):
        adapter = _mock_adapter("Output.")
        chunker = TextChunker(chunk_size=10000, overlap=200)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("Some content.")

        result = asyncio.run(pipeline.run(doc, TaskType.SUMMARIZE))

        assert result.model == "mock-model"
        assert result.provider == "mock"

    def test_document_reference_preserved(self):
        adapter = _mock_adapter("Output.")
        chunker = TextChunker(chunk_size=10000, overlap=200)
        pipeline = ProcessingPipeline(adapter, chunker)
        doc = DocumentLoader.load_text("Some content.", filename="my_doc.txt")

        result = asyncio.run(pipeline.run(doc, TaskType.SUMMARIZE))

        assert result.document.filename == "my_doc.txt"


class TestDocumentLoader:
    """Quick loader tests (complement the pipeline tests)."""

    def test_load_text_basic(self):
        doc = DocumentLoader.load_text("Hello world")
        assert doc.content == "Hello world"
        assert doc.word_count == 2
        assert doc.char_count == 11

    def test_load_text_strips_whitespace(self):
        doc = DocumentLoader.load_text("  padded  ")
        assert doc.content == "padded"

    def test_load_text_empty_rejected(self):
        with pytest.raises(ValueError, match="empty"):
            DocumentLoader.load_text("")

    def test_load_text_whitespace_only_rejected(self):
        with pytest.raises(ValueError, match="empty"):
            DocumentLoader.load_text("   \n\n  ")

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            DocumentLoader.load("/nonexistent/path/file.txt")

    def test_load_unsupported_extension(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"data")
            path = f.name
        with pytest.raises(ValueError, match="Unsupported"):
            DocumentLoader.load(path)


# ── Quality Check Tests ──────────────────────────────────────────────────────

from mcp.types import TextContent, CreateMessageResult
from transsum.mcp.server import _quality_check, _check_roots


def _mock_ctx(response_text: str) -> MagicMock:
    """Create a mock MCP context whose session returns the given text."""
    ctx = MagicMock()
    result = CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text=response_text),
        model="test-model",
    )
    ctx.session.create_message = AsyncMock(return_value=result)
    return ctx


class TestQualityCheck:
    """Tests for the _quality_check sampling helper."""

    def test_pass_response(self):
        ctx = _mock_ctx("PASS — the summary captures all key points accurately.")
        result = asyncio.run(_quality_check(ctx, "A good summary.", "Source text here."))
        assert result["quality_review"] == "pass"
        assert "PASS" in result["quality_note"]

    def test_fail_response(self):
        ctx = _mock_ctx("FAIL — the summary misses the main argument.")
        result = asyncio.run(_quality_check(ctx, "A bad summary.", "Source text here."))
        assert result["quality_review"] == "fail"
        assert "FAIL" in result["quality_note"]

    def test_ctx_none_skips(self):
        result = asyncio.run(_quality_check(None, "Any summary.", "Any source."))
        assert result["quality_review"] == "skipped"

    def test_sampling_exception_skips(self):
        ctx = MagicMock()
        ctx.session.create_message = AsyncMock(side_effect=Exception("not supported"))
        result = asyncio.run(_quality_check(ctx, "Summary.", "Source."))
        assert result["quality_review"] == "skipped"


# ── Roots Validation Tests ──────────────────────────────────────────────────


def _mock_roots_ctx(root_uris: list[str]) -> MagicMock:
    """Create a mock MCP context whose session returns the given roots."""
    ctx = MagicMock()
    roots = []
    for uri in root_uris:
        root = MagicMock()
        root.uri = uri
        roots.append(root)
    result = MagicMock()
    result.roots = roots
    ctx.session.list_roots = AsyncMock(return_value=result)
    return ctx


class TestCheckRoots:
    """Tests for the _check_roots path validation helper."""

    def test_path_within_root_allowed(self, tmp_path):
        file = tmp_path / "docs" / "notes.txt"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()
        ctx = _mock_roots_ctx([f"file://{tmp_path}"])
        asyncio.run(_check_roots(ctx, str(file)))  # Should not raise

    def test_path_outside_root_denied(self, tmp_path):
        ctx = _mock_roots_ctx([f"file://{tmp_path / 'allowed'}"])
        with pytest.raises(ValueError, match="Access denied"):
            asyncio.run(_check_roots(ctx, "/some/other/path/secret.txt"))

    def test_ctx_none_allows_access(self):
        asyncio.run(_check_roots(None, "/any/path.txt"))  # Should not raise

    def test_list_roots_exception_allows_access(self):
        ctx = MagicMock()
        ctx.session.list_roots = AsyncMock(side_effect=Exception("unsupported"))
        asyncio.run(_check_roots(ctx, "/any/path.txt"))  # Should not raise

    def test_empty_roots_allows_access(self):
        ctx = _mock_roots_ctx([])
        asyncio.run(_check_roots(ctx, "/any/path.txt"))  # Should not raise