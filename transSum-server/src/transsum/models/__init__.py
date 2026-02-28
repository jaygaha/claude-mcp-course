"""Model adapters — unified interface over Ollama & Anthropic."""

from transsum.models.base import BaseModelAdapter, ModelResponse
from transsum.models.factory import create_adapter

__all__ = ["BaseModelAdapter", "ModelResponse", "create_adapter"]