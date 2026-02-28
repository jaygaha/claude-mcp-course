"""
Centralised, validated application configuration.

All values are loaded from environment variables (or a .env file).
Pydantic validates types, applies defaults, and raises clear
errors when required values are missing or out of range.

Usage:
    from transsum.config import get_settings
    settings = get_settings()
    print(settings.model_provider)   # → "ollama"
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Walk up from this file to find the project-root .env
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path, override=True)


# ── Enums ───────────────────────────────────────────────────────────────────

class ModelProvider(str, Enum):
    """Supported LLM backends."""
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


# ── Settings ────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """
    Single source of truth for every tunable parameter.

    Environment variable names match field names in UPPER_CASE.
    Example:  model_provider  ←→  MODEL_PROVIDER
    """

    # ── Provider Selection ──────────────────────────────────────────────
    model_provider: ModelProvider = Field(
        default=ModelProvider.OLLAMA,
        description="Active LLM backend: 'ollama' or 'anthropic'.",
    )

    # ── Ollama ──────────────────────────────────────────────────────────
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL of the local Ollama server.",
    )
    ollama_model: str = Field(
        default="llama3.1",
        description="Ollama model tag to use (e.g. llama3.1, mistral).",
    )

    # ── Anthropic ───────────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key (required when provider=anthropic).",
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Anthropic model identifier.",
    )

    # ── Processing ──────────────────────────────────────────────────────
    chunk_size: int = Field(
        default=4000, ge=500, le=32000,
        description="Maximum character count per text chunk.",
    )
    chunk_overlap: int = Field(
        default=200, ge=0, le=2000,
        description="Characters of overlap between consecutive chunks.",
    )
    max_retries: int = Field(
        default=3, ge=1, le=10,
        description="Number of retry attempts for failed LLM calls.",
    )
    request_timeout: int = Field(
        default=120, ge=10, le=600,
        description="HTTP timeout in seconds for LLM requests.",
    )

    # ── Logging ─────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    # ── MCP ─────────────────────────────────────────────────────────────
    mcp_server_port: int = Field(default=8765, ge=1024, le=65535)
    mcp_transport: Literal["stdio", "streamable-http"] = Field(
        default="stdio",
        description="MCP transport: 'stdio' for local clients, 'streamable-http' for remote.",
    )

    # ── Validators ──────────────────────────────────────────────────────

    @field_validator("anthropic_api_key")
    @classmethod
    def _require_api_key_for_anthropic(cls, v, info):
        """Fail fast if Anthropic is selected but no key is provided."""
        provider = info.data.get("model_provider")
        if provider == ModelProvider.ANTHROPIC and not v:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when MODEL_PROVIDER=anthropic. "
                "Set it in your .env file."
            )
        return v

    @field_validator("chunk_overlap")
    @classmethod
    def _overlap_less_than_size(cls, v, info):
        size = info.data.get("chunk_size", 4000)
        if v >= size:
            raise ValueError(
                f"CHUNK_OVERLAP ({v}) must be less than CHUNK_SIZE ({size})."
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        use_enum_values=True,
    )


# ── Factory ─────────────────────────────────────────────────────────────────

def get_settings() -> Settings:
    """Return a validated Settings instance."""
    return Settings()