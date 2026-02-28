"""
Adapter for locally-running Ollama servers.

Communicates over HTTP using the /api/chat endpoint.
Supports both batch (full response) and streaming modes.

Ollama API docs: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

from __future__ import annotations

import json
import logging
from typing import AsyncIterator

import httpx

from transsum.models.base import BaseModelAdapter, ModelResponse

logger = logging.getLogger(__name__)


class OllamaAdapter(BaseModelAdapter):
    """Async adapter for Ollama's local chat API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1",
        timeout: int = 120,
        max_retries: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
        )
        logger.info(
            "OllamaAdapter ready → %s (model: %s, timeout: %ds)",
            base_url, model, timeout,
        )

    # ── Batch Generation ────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Send prompt to Ollama and return the full response."""
        messages = self._build_messages(prompt, system)
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post("/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()

                return ModelResponse(
                    text=data["message"]["content"],
                    model=self._model,
                    provider="ollama",
                    usage={
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                    },
                    finish_reason=data.get("done_reason"),
                )

            except httpx.ConnectError as exc:
                last_error = exc
                logger.warning(
                    "Ollama connection failed (attempt %d/%d). "
                    "Is Ollama running at %s?",
                    attempt, self._max_retries, self._base_url,
                )
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.warning(
                    "Ollama HTTP %d (attempt %d/%d): %s",
                    exc.response.status_code, attempt, self._max_retries, exc,
                )
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(
                    "Ollama timeout (attempt %d/%d)", attempt, self._max_retries,
                )

        raise RuntimeError(
            f"Ollama request failed after {self._max_retries} attempts: {last_error}"
        ) from last_error

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
        messages = self._build_messages(prompt, system)
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with self._client.stream("POST", "/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token

    # ── Helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_messages(prompt: str, system: str) -> list[dict]:
        """Construct the messages array for Ollama's chat API."""
        msgs: list[dict] = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        return msgs

    async def close(self) -> None:
        """Shut down the underlying HTTP client."""
        await self._client.aclose()
        logger.debug("OllamaAdapter closed.")