"""Tests for the model adapter factory."""

import os
import pytest
from transsum.config import Settings
from transsum.models.factory import create_adapter
from transsum.models.ollama import OllamaAdapter
from transsum.models.anthropic_adapter import AnthropicAdapter


class TestFactory:
    """Verify the factory creates the correct adapter type."""

    def setup_method(self):
        os.environ.pop("MODEL_PROVIDER", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_ollama_by_default(self):
        settings = Settings()
        adapter = create_adapter(settings)
        assert isinstance(adapter, OllamaAdapter)

    def test_explicit_ollama(self):
        os.environ["MODEL_PROVIDER"] = "ollama"
        settings = Settings()
        adapter = create_adapter(settings)
        assert isinstance(adapter, OllamaAdapter)

    def test_anthropic_with_key(self):
        os.environ["MODEL_PROVIDER"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        settings = Settings()
        adapter = create_adapter(settings)
        assert isinstance(adapter, AnthropicAdapter)

    def test_ollama_respects_custom_model(self):
        os.environ["MODEL_PROVIDER"] = "ollama"
        os.environ["OLLAMA_MODEL"] = "mistral"
        settings = Settings()
        adapter = create_adapter(settings)
        assert isinstance(adapter, OllamaAdapter)
        assert adapter._model == "mistral"

    def test_ollama_respects_custom_url(self):
        os.environ["MODEL_PROVIDER"] = "ollama"
        os.environ["OLLAMA_BASE_URL"] = "http://gpu-server:11434"
        settings = Settings()
        adapter = create_adapter(settings)
        assert "gpu-server" in adapter._base_url