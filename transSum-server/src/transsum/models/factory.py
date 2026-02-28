"""
Model adapter factory.

This is the ONLY place that decides which concrete adapter to
instantiate. Every other module depends on BaseModelAdapter alone,
making provider-switching a pure configuration concern.
"""

from __future__ import annotations

from transsum.config import ModelProvider, Settings
from transsum.models.base import BaseModelAdapter


def create_adapter(settings: Settings) -> BaseModelAdapter:
    """
    Instantiate the correct adapter based on current configuration.

    Args:
        settings: Validated application settings.

    Returns:
        A ready-to-use adapter instance.

    Raises:
        ValueError: If the provider name is not recognised.
    """
    if settings.model_provider == ModelProvider.OLLAMA:
        from transsum.models.ollama import OllamaAdapter

        return OllamaAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.request_timeout,
            max_retries=settings.max_retries,
        )

    if settings.model_provider == ModelProvider.ANTHROPIC:
        from transsum.models.anthropic_adapter import AnthropicAdapter

        return AnthropicAdapter(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            timeout=settings.request_timeout,
            max_retries=settings.max_retries,
        )

    raise ValueError(f"Unknown model provider: {settings.model_provider!r}")