"""
Adapter for Anthropic's Messages API (Claude family).

Uses the official `anthropic` Python SDK with full async support
and native streaming via the .stream() context manager.

Docs: https://docs.anthropic.com/en/api/messages
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

import anthropic

from transsum.models.base import BaseModelAdapter, ModelResponse

logger = logging.getLogger(__name__)


class AnthropicAdapter(BaseModelAdapter):
    """Async adapter for the Anthropic Messages API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        timeout: int = 120,
        max_retries: int = 3,
    ) -> None:
        self._model = model
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        logger.info("AnthropicAdapter ready → model: %s", model)

    # ── Batch Generation ────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Send prompt to Anthropic and return the full response."""
        kwargs: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        try:
            message = await self._client.messages.create(**kwargs)
        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Anthropic authentication failed. Check your ANTHROPIC_API_KEY."
            )
        except anthropic.RateLimitError:
            raise RuntimeError(
                "Anthropic rate limit reached. Wait a moment and retry."
            )

        return ModelResponse(
            text=message.content[0].text,
            model=self._model,
            provider="anthropic",
            usage={
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens,
            },
            finish_reason=message.stop_reason,
        )

    # ── Streaming ───────────────────────────────────────────────────────

    async def stream(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream response tokens one at a time."""
        kwargs: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    # ── Cleanup ─────────────────────────────────────────────────────────

    async def close(self) -> None:
        """Shut down the underlying HTTP client."""
        await self._client.close()
        logger.debug("AnthropicAdapter closed.")