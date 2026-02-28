"""Tests for the configuration layer."""

import os
import pytest
from transsum.config import Settings, ModelProvider


class TestSettingsDefaults:
    """Verify sensible defaults and basic validation."""

    def setup_method(self):
        """Clear provider-related env vars before each test."""
        for key in ["MODEL_PROVIDER", "ANTHROPIC_API_KEY", "CHUNK_SIZE", "CHUNK_OVERLAP"]:
            os.environ.pop(key, None)

    def test_default_provider_is_ollama(self):
        s = Settings()
        assert s.model_provider == "ollama"

    def test_default_ollama_url(self):
        s = Settings()
        assert s.ollama_base_url == "http://localhost:11434"

    def test_default_chunk_settings(self):
        s = Settings()
        assert s.chunk_size == 4000
        assert s.chunk_overlap == 200


class TestAnthropicValidation:
    """Ensure Anthropic config is validated properly."""

    def setup_method(self):
        # Must explicitly blank the key — load_dotenv may have injected it
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_anthropic_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
        with pytest.raises(Exception, match="ANTHROPIC_API_KEY"):
            Settings(_env_file=None)

    def test_anthropic_with_valid_key(self, monkeypatch):
        monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-123")
        s = Settings(_env_file=None)
        assert s.model_provider == "anthropic"
        assert s.anthropic_api_key == "sk-ant-test-key-123"

    def test_ollama_ignores_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("MODEL_PROVIDER", "ollama")
        s = Settings(_env_file=None)  # Should NOT raise
        assert s.anthropic_api_key is None


class TestChunkValidation:
    """Ensure chunk parameters are bounded correctly."""

    def setup_method(self):
        os.environ["MODEL_PROVIDER"] = "ollama"
        for key in ["CHUNK_SIZE", "CHUNK_OVERLAP"]:
            os.environ.pop(key, None)

    def test_chunk_size_below_minimum_rejected(self):
        os.environ["CHUNK_SIZE"] = "100"
        with pytest.raises(Exception):
            Settings()

    def test_chunk_size_above_maximum_rejected(self):
        os.environ["CHUNK_SIZE"] = "50000"
        with pytest.raises(Exception):
            Settings()

    def test_overlap_must_be_less_than_size(self):
        os.environ["CHUNK_SIZE"] = "1000"
        os.environ["CHUNK_OVERLAP"] = "1000"
        with pytest.raises(Exception):
            Settings()

    def test_valid_chunk_config(self):
        os.environ["CHUNK_SIZE"] = "2000"
        os.environ["CHUNK_OVERLAP"] = "100"
        s = Settings()
        assert s.chunk_size == 2000
        assert s.chunk_overlap == 100