"""
MCP Server — exposes transSum tools via FastMCP (stdio or StreamableHTTP).

Run standalone (stdio, default):
    python -m transsum.mcp.server

Run with StreamableHTTP transport:
    python -m transsum.mcp.server streamable-http

Register in claude_desktop_config.json:
    {
        "mcpServers": {
            "transsum": {
                "command": "python",
                "args": ["-m", "transsum.mcp.server"]
            }
        }
    }
"""

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent
from mcp.server.fastmcp.prompts.base import Message, UserMessage
from pydantic import Field

from transsum.config import ModelProvider, get_settings
from transsum.models.factory import create_adapter
from transsum.processing.loader import DocumentLoader, _FORMAT_READERS
from transsum.processing.chunker import TextChunker
from transsum.processing.pipeline import ProcessingPipeline, TaskType

_settings = get_settings()
mcp = FastMCP("transsum", log_level="ERROR", port=_settings.mcp_server_port)


async def _build_pipeline() -> tuple[ProcessingPipeline, Any]:
    """Create a pipeline + adapter from current config."""
    settings = get_settings()
    adapter = create_adapter(settings)
    chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
    pipeline = ProcessingPipeline(adapter, chunker)
    return pipeline, adapter


_QUALITY_SYSTEM = (
    "You are a summary quality reviewer. Evaluate whether the summary "
    "accurately captures the key points of the source text. "
    "Respond with exactly PASS or FAIL on the first line, "
    "followed by a brief explanation."
)


async def _quality_check(
    ctx: Context | None, summary: str, source_text: str
) -> dict:
    """Use client-side sampling to review summary quality."""
    if ctx is None:
        return {"quality_review": "skipped"}
    try:
        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Source text:\n{source_text[:2000]}\n\n"
                            f"Summary:\n{summary}\n\n"
                            "Rate this summary as PASS or FAIL."
                        ),
                    ),
                )
            ],
            max_tokens=256,
            system_prompt=_QUALITY_SYSTEM,
        )
        response_text = (
            result.content.text
            if hasattr(result.content, "text")
            else str(result.content)
        )
        passed = response_text.strip().upper().startswith("PASS")
        return {
            "quality_review": "pass" if passed else "fail",
            "quality_note": response_text.strip(),
        }
    except Exception:
        return {"quality_review": "skipped"}


def _file_url_to_path(file_url) -> Path:
    """Convert a file:// URL to a filesystem Path."""
    parsed = urlparse(str(file_url))
    path = unquote(parsed.path)
    if len(path) > 2 and path[0] == "/" and path[2] == ":":
        path = path[1:]  # Windows: /C:/... → C:/...
    return Path(path)


async def _check_roots(ctx: Context | None, file_path: str) -> None:
    """Validate that file_path is within one of the client's approved roots."""
    if ctx is None:
        return
    try:
        roots_result = await ctx.session.list_roots()
    except Exception:
        return  # Client doesn't support roots — allow access
    if not roots_result.roots:
        return  # No roots declared — allow access
    resolved = Path(file_path).resolve()
    for root in roots_result.roots:
        root_path = _file_url_to_path(root.uri)
        try:
            resolved.relative_to(root_path)
            return  # File is under this root — allowed
        except ValueError:
            continue
    allowed = [str(_file_url_to_path(r.uri)) for r in roots_result.roots]
    raise ValueError(
        f"Access denied: '{resolved}' is outside the allowed directories.\n"
        f"Allowed roots: {', '.join(allowed)}"
    )


# ── Resources ────────────────────────────────────────────────────────────────


@mcp.resource("transsum://config", mime_type="application/json")
def get_config() -> str:
    """Current server configuration (API keys are masked)."""
    settings = get_settings()
    return json.dumps({
        "provider": settings.model_provider,
        "model": (
            settings.ollama_model
            if settings.model_provider == ModelProvider.OLLAMA
            else settings.anthropic_model
        ),
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "max_retries": settings.max_retries,
        "timeout": settings.request_timeout,
        "api_key_set": settings.anthropic_api_key is not None,
    }, indent=2)


@mcp.resource("transsum://supported-formats", mime_type="application/json")
def get_supported_formats() -> str:
    """File formats the server can ingest, grouped by category."""
    categories: dict[str, list[str]] = {}
    for ext, reader in _FORMAT_READERS.items():
        category = "pdf" if "pdf" in reader else "text"
        categories.setdefault(category, []).append(ext)
    return json.dumps(categories, indent=2)


@mcp.resource("transsum://providers", mime_type="application/json")
def get_providers() -> str:
    """Available LLM providers and their current settings."""
    settings = get_settings()
    return json.dumps({
        "ollama": {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        },
        "anthropic": {
            "model": settings.anthropic_model,
            "api_key_set": settings.anthropic_api_key is not None,
        },
        "active_provider": settings.model_provider,
    }, indent=2)


@mcp.resource("transsum://config/{key}", mime_type="text/plain")
def get_config_key(key: str) -> str:
    """Look up a single configuration value by key name."""
    settings = get_settings()
    allowed = {
        "provider": settings.model_provider,
        "model": (
            settings.ollama_model
            if settings.model_provider == ModelProvider.OLLAMA
            else settings.anthropic_model
        ),
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "max_retries": settings.max_retries,
        "timeout": settings.request_timeout,
    }
    if key not in allowed:
        raise ValueError(
            f"Unknown config key '{key}'. Valid keys: {', '.join(sorted(allowed))}"
        )
    return str(allowed[key])


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def summarize_text(
    text: str = Field(description="The text content to summarize"),
    ctx: Context = None,
) -> str:
    """Summarize a block of text into a concise, structured summary.
    Handles long texts automatically via intelligent chunking."""
    pipeline, adapter = await _build_pipeline()
    try:
        doc = DocumentLoader.load_text(text)
        result = await pipeline.run(doc, TaskType.SUMMARIZE, ctx=ctx)
        quality = await _quality_check(ctx, result.output, text)
        return json.dumps({
            "summary": result.output,
            "model": result.model,
            "provider": result.provider,
            "chunks_processed": result.chunks_processed,
            **quality,
        }, indent=2, ensure_ascii=False)
    finally:
        await adapter.close()


@mcp.tool()
async def translate_text(
    text: str = Field(description="The text to translate"),
    target_language: str = Field(default="English", description="Target language (e.g. 'English', 'Japanese')"),
    ctx: Context = None,
) -> str:
    """Translate text into a specified target language.
    Supports any language pair the underlying model handles."""
    pipeline, adapter = await _build_pipeline()
    try:
        doc = DocumentLoader.load_text(text)
        result = await pipeline.run(doc, TaskType.TRANSLATE, language=target_language, ctx=ctx)
        return json.dumps({
            "translation": result.output,
            "target_language": target_language,
            "model": result.model,
            "provider": result.provider,
            "chunks_processed": result.chunks_processed,
        }, indent=2, ensure_ascii=False)
    finally:
        await adapter.close()


@mcp.tool()
async def summarize_file(
    file_path: str = Field(description="Absolute or relative path to the document file"),
    ctx: Context = None,
) -> str:
    """Load a document file and produce a summary.
    Supports .txt, .md, .pdf, .html, .csv, .json files."""
    pipeline, adapter = await _build_pipeline()
    try:
        await _check_roots(ctx, file_path)
        doc = DocumentLoader.load(file_path)
        result = await pipeline.run(doc, TaskType.SUMMARIZE, ctx=ctx)
        quality = await _quality_check(ctx, result.output, doc.content)
        return json.dumps({
            "summary": result.output,
            "filename": doc.filename,
            "word_count": doc.word_count,
            "model": result.model,
            "provider": result.provider,
            "chunks_processed": result.chunks_processed,
            **quality,
        }, indent=2, ensure_ascii=False)
    finally:
        await adapter.close()


# ── Prompts ───────────────────────────────────────────────────────────────────


@mcp.prompt(
    name="summarize",
    description="Summarize a block of text into a concise, structured summary",
)
def summarize_prompt(text: str) -> list[Message]:
    return [
        UserMessage(
            content=(
                "Please summarize the following text using the summarize_text tool. "
                "Provide a clear, structured summary preserving key facts and conclusions."
                f"\n\n{text}"
            )
        )
    ]


@mcp.prompt(
    name="translate",
    description="Translate text into a target language",
)
def translate_prompt(text: str, language: str = "English") -> list[Message]:
    return [
        UserMessage(
            content=(
                f"Please translate the following text into {language} using the translate_text tool. "
                "Preserve the original meaning, tone, and formatting."
                f"\n\n{text}"
            )
        )
    ]


@mcp.prompt(
    name="summarize_from_file",
    description="Load and summarize a document file",
)
def summarize_from_file_prompt(file_path: str) -> list[Message]:
    return [
        UserMessage(
            content=(
                f"Please summarize the document at '{file_path}' using the summarize_file tool. "
                "Provide a clear, structured summary preserving key facts and conclusions."
            )
        )
    ]


if __name__ == "__main__":
    _valid = ("stdio", "streamable-http")
    if len(sys.argv) > 1:
        _transport = sys.argv[1]
        if _transport not in _valid:
            print(
                "Usage: python -m transsum.mcp.server [stdio|streamable-http]",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        _transport = _settings.mcp_transport

    if _transport == "streamable-http":
        print(
            f"Starting transsum MCP server on "
            f"http://127.0.0.1:{_settings.mcp_server_port}/mcp",
            file=sys.stderr,
        )

    mcp.run(transport=_transport)
