"""
Abstract base class that every LLM adapter must implement.

This guarantees the rest of the codebase never touches a vendor SDK
directly — swapping backends only requires a new adapter subclass
and a one-line addition to the factory.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional


@dataclass
class ModelResponse:
    """
    Unified response envelope returned by every adapter.

    Attributes:
        text:           The generated text content.
        model:          Identifier of the model that produced the response.
        provider:       Which backend was used ("ollama" / "anthropic").
        usage:          Token counts — {"prompt_tokens": N, "completion_tokens": N}.
        finish_reason:  Why generation stopped (e.g. "stop", "length").
    """
    text: str
    model: str
    provider: str
    usage: dict = field(default_factory=dict)
    finish_reason: Optional[str] = None


class BaseModelAdapter(abc.ABC):
    """
    Contract for LLM adapters.

    Every concrete adapter (Ollama, Anthropic, future providers)
    must implement these three methods.
    """

    @abc.abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Send a single prompt and return the complete response."""

    @abc.abstractmethod
    async def stream(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Yield response tokens incrementally as they arrive."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Release held resources (HTTP connections, etc.)."""