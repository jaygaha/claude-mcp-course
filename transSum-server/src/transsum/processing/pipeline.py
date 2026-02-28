"""
Processing pipeline — orchestrates the full document-to-output flow.

Short documents:  Single LLM call (fast path).
Long documents:   Map-Reduce pattern:
                    1. MAP   — process each chunk independently
                    2. REDUCE — merge partial results into one coherent output

Supports both summarisation and translation tasks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Callable
from typing import AsyncIterator

from mcp.server.fastmcp import Context

from transsum.models.base import BaseModelAdapter, ModelResponse
from transsum.processing.chunker import Chunk, TextChunker
from transsum.processing.loader import Document

logger = logging.getLogger(__name__)


# ── Task Types ──────────────────────────────────────────────────────────────

class TaskType(str, Enum):
    SUMMARIZE = "summarize"
    TRANSLATE = "translate"


# ── Result Container ────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    """Final output of a pipeline run."""
    task: TaskType
    output: str
    document: Document
    chunks_processed: int
    model: str
    provider: str
    usage: dict = field(default_factory=dict)


# ── Prompt Templates ────────────────────────────────────────────────────────

_SYSTEM_PROMPTS = {
    TaskType.SUMMARIZE: (
        "You are an expert document analyst. Produce clear, accurate, "
        "and well-structured summaries. Preserve key facts, figures, "
        "and conclusions. Use markdown formatting where it aids readability."
    ),
    TaskType.TRANSLATE: (
        "You are a professional translator. Produce natural, fluent "
        "translations that preserve the original meaning, tone, and "
        "formatting. Output ONLY the translation — no commentary."
    ),
}

_CHUNK_SUMMARIZE = (
    "Summarize the following text section (chunk {idx} of {total}).\n"
    "Focus on key points and important details.\n\n"
    "---\n{text}\n---"
)

_FINAL_SUMMARIZE = (
    "Below are summaries of consecutive sections of a document "
    'titled "{filename}".\n\n'
    "Combine them into ONE coherent, well-structured summary.\n"
    "Eliminate redundancy. Use markdown headings where appropriate.\n\n"
    "{combined}"
)

_CHUNK_TRANSLATE = (
    "Translate the following text into **{language}** "
    "(chunk {idx} of {total}).\n\n"
    "---\n{text}\n---"
)

_FINAL_TRANSLATE = (
    "Below are translated sections of a document. "
    "Combine them into one coherent, flowing text. "
    "Fix any seam artifacts between chunks.\n\n"
    "{combined}"
)


# ── Pipeline ────────────────────────────────────────────────────────────────

class ProcessingPipeline:
    """
    Orchestrates document → chunks → LLM → merged output.

    Usage:
        adapter  = create_adapter(settings)
        chunker  = TextChunker(settings.chunk_size, settings.chunk_overlap)
        pipeline = ProcessingPipeline(adapter, chunker)
        result   = await pipeline.run(document, TaskType.SUMMARIZE)
    """

    def __init__(
        self,
        adapter: BaseModelAdapter,
        chunker: TextChunker,
    ) -> None:
        self._adapter = adapter
        self._chunker = chunker

    # ── Main Entry Point ────────────────────────────────────────────────

    async def run(
        self,
        document: Document,
        task: TaskType,
        *,
        language: str = "English",
        temperature: float = 0.3,
        ctx: Context | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> PipelineResult:
        """
        Execute the full pipeline.

        Args:
            document:    Loaded document to process.
            task:        SUMMARIZE or TRANSLATE.
            language:    Target language (only used for TRANSLATE).
            temperature: LLM sampling temperature.
            ctx:         Optional MCP Context for progress/log notifications.
            on_progress: Optional callback receiving a status message string.

        Returns:
            PipelineResult with the final output and metadata.
        """
        chunks = self._chunker.chunk(document.content)
        system = _SYSTEM_PROMPTS[task]
        total = len(chunks)

        logger.info(
            "Pipeline start: task=%s, file=%s, chunks=%d",
            task.value, document.filename, total,
        )

        # Helper to emit status to both MCP and CLI callers
        def _notify(msg: str) -> None:
            if on_progress:
                on_progress(msg)

        # ── Fast path: single chunk ────────────────────────────────────
        if total == 1:
            if ctx:
                await ctx.report_progress(0, 1)
                await ctx.info("Processing single chunk...")
            _notify("Processing with LLM…")
            prompt = self._make_chunk_prompt(task, chunks[0], 1, 1, language)
            resp = await self._adapter.generate(
                prompt, system=system, temperature=temperature,
            )
            if ctx:
                await ctx.report_progress(1, 1)
                await ctx.info("Complete")
            _notify("Complete")
            return PipelineResult(
                task=task,
                output=resp.text,
                document=document,
                chunks_processed=1,
                model=resp.model,
                provider=resp.provider,
                usage=resp.usage,
            )

        # ── MAP phase: process each chunk ──────────────────────────────
        total_steps = total + 1  # N chunks + 1 reduce step
        partial_results: list[str] = []
        total_usage: dict = {"prompt_tokens": 0, "completion_tokens": 0}

        if ctx:
            await ctx.report_progress(0, total_steps)
            await ctx.info(f"Document split into {total} chunks")
        _notify(f"Document split into {total} chunks")

        for i, chunk in enumerate(chunks, 1):
            logger.debug("Processing chunk %d/%d (%d chars)…", i, total, chunk.char_count)
            _notify(f"Processing chunk {i}/{total}…")
            prompt = self._make_chunk_prompt(task, chunk, i, total, language)
            resp = await self._adapter.generate(
                prompt, system=system, temperature=temperature,
            )
            partial_results.append(resp.text)
            for k in total_usage:
                total_usage[k] += resp.usage.get(k, 0)
            if ctx:
                await ctx.report_progress(i, total_steps)
                await ctx.info(f"Processed chunk {i}/{total}")
            _notify(f"Processed chunk {i}/{total}")

        # ── REDUCE phase: merge partials ───────────────────────────────
        if ctx:
            await ctx.info(f"Merging {total} sections into final output...")
        _notify(f"Merging {total} sections into final output…")

        combined = "\n\n---\n\n".join(
            f"**Section {i}:**\n{text}"
            for i, text in enumerate(partial_results, 1)
        )

        if task == TaskType.SUMMARIZE:
            merge_prompt = _FINAL_SUMMARIZE.format(
                filename=document.filename, combined=combined,
            )
        else:
            merge_prompt = _FINAL_TRANSLATE.format(combined=combined)

        logger.debug("Running reduce step…")
        final = await self._adapter.generate(
            merge_prompt, system=system, temperature=temperature,
        )
        for k in total_usage:
            total_usage[k] += final.usage.get(k, 0)

        if ctx:
            await ctx.report_progress(total_steps, total_steps)
            await ctx.info("Complete")

        logger.info(
            "Pipeline complete: %d chunks, %d total tokens",
            total, sum(total_usage.values()),
        )

        return PipelineResult(
            task=task,
            output=final.text,
            document=document,
            chunks_processed=total,
            model=final.model,
            provider=final.provider,
            usage=total_usage,
        )

    # ── Streaming (used by Phase 2 UI later) ───────────────────────────

    async def stream_run(
        self,
        document: Document,
        task: TaskType,
        *,
        language: str = "English",
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        """
        Stream tokens for single-chunk docs.
        Falls back to batch + yield for multi-chunk docs.
        """
        chunks = self._chunker.chunk(document.content)
        system = _SYSTEM_PROMPTS[task]

        if len(chunks) == 1:
            prompt = self._make_chunk_prompt(task, chunks[0], 1, 1, language)
            async for token in self._adapter.stream(
                prompt, system=system, temperature=temperature,
            ):
                yield token
        else:
            result = await self.run(
                document, task, language=language, temperature=temperature,
            )
            yield result.output

    # ── Prompt Construction ─────────────────────────────────────────────

    @staticmethod
    def _make_chunk_prompt(
        task: TaskType,
        chunk: Chunk,
        idx: int,
        total: int,
        language: str,
    ) -> str:
        """Build the appropriate prompt for a single chunk."""
        if task == TaskType.SUMMARIZE:
            return _CHUNK_SUMMARIZE.format(
                idx=idx, total=total, text=chunk.text,
            )
        return _CHUNK_TRANSLATE.format(
            idx=idx, total=total, text=chunk.text, language=language,
        )