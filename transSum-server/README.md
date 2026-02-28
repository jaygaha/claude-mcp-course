# transSum — AI Document Summarizer & Translator

A modular Python application that summarizes and translates documents using locally-deployed Ollama models or the Anthropic API, with full MCP (Model Context Protocol) integration.

## Features

- **Summarize** documents or inline text into concise, structured summaries
- **Translate** text into any language the underlying model supports
- **Multi-format** ingestion — `.txt`, `.md`, `.html`, `.csv`, `.json`, and `.pdf` (requires `pypdf`)
- **Intelligent chunking** — sentence-aware splitting with overlap for long documents
- **Map-reduce pipeline** — processes large documents in chunks, then merges results
- **Dual LLM backends** — Ollama (local) or Anthropic Claude (cloud)
- **MCP server** — expose tools and resources over stdio for Claude Desktop or any MCP client
- **Rich CLI output** — formatted panels, spinners, and token usage stats

## Project Structure

```
transSum-server/
├── .env.example                ← copy to .env and configure
├── pyproject.toml              ← dependencies & entry point
├── src/
│   └── transsum/
│       ├── __init__.py
│       ├── config.py           ← Pydantic-validated settings
│       ├── cli.py              ← Basic CLI
│       ├── models/
│       │   ├── base.py         ← abstract adapter interface
│       │   ├── ollama.py       ← Ollama HTTP adapter
│       │   ├── anthropic_adapter.py
│       │   └── factory.py      ← provider-aware factory
│       ├── processing/
│       │   ├── loader.py       ← document ingestion (txt/md/pdf/…)
│       │   ├── chunker.py      ← sentence-aware text splitting
│       │   └── pipeline.py     ← map-reduce orchestration
│       └── mcp/
│           └── server.py       ← MCP stdio server (FastMCP)
└── tests/
    ├── test_config.py
    ├── test_chunker.py
    ├── test_models.py
    └── test_pipeline.py
```

## Prerequisites

- **Python 3.14+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **Ollama** (for local models) — [install guide](https://ollama.com/download)
- **Anthropic API key** (optional, for Claude models)

## Installation

```bash
# Clone and navigate to the project
cd transSum-server

# Copy the example config and edit with your settings
cp .env.example .env

# Install dependencies
uv sync

# Install dev dependencies (for testing and linting)
uv sync --group dev
```

## Supported Formats

| Format | Extensions | Status |
|--------|-----------|--------|
| Plain text | `.txt`, `.md` | Built-in |
| Markup / data | `.html`, `.csv`, `.json` | Built-in |
| PDF | `.pdf` | Requires `pypdf` — included in dependencies, run `uv sync` to install |

> **PDF not working?** Run `uv sync` to ensure `pypdf` is installed. If you still get an `ImportError`, verify with `uv pip list | grep pypdf`.

## Configuration

All settings are managed via environment variables or the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PROVIDER` | `ollama` | LLM backend: `ollama` or `anthropic` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model tag |
| `ANTHROPIC_API_KEY` | — | Required when provider is `anthropic` |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model identifier |
| `CHUNK_SIZE` | `4000` | Max characters per text chunk (500–32,000) |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks (0–2,000, must be < chunk size) |
| `MAX_RETRIES` | `3` | Retry attempts for failed LLM calls (1–10) |
| `REQUEST_TIMEOUT` | `120` | HTTP timeout in seconds (10–600) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MCP_SERVER_PORT` | `8765` | MCP server port (1024–65535) |
| `MCP_TRANSPORT` | `stdio` | MCP transport: `stdio` or `streamable-http` |

### Provider Setup

**Ollama (local):**

```bash
# Pull a model
ollama pull llama3.1

# Verify it's running
curl http://localhost:11434/api/tags
```

**Anthropic (cloud):**

```bash
# Set your API key in .env
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## CLI Usage

The CLI provides three commands: `summarize`, `translate`, and `config`.

### Summarize

```bash
# Summarize a file
uv run transsum summarize notes.md

# Summarize inline text
uv run transsum summarize --text "Your long article content here..."

# Override provider and model
uv run transsum summarize report.txt --provider anthropic --model claude-sonnet-4-20250514
```

### Translate

```bash
# Translate a file to French
uv run transsum translate article.txt --language French

# Translate inline text to Japanese
uv run transsum translate --text "Hello world" -l Japanese

# Translate with a specific provider
uv run transsum translate paper.txt -l German -p anthropic
```

### View Config

```bash
uv run transsum config
```

Displays a formatted table of all active settings, including provider, model, chunk parameters, and API key status.

### Global Options

```bash
uv run transsum --version              # Show version
uv run transsum --log-level DEBUG ...  # Set log verbosity (DEBUG|INFO|WARNING|ERROR)
```

## MCP Server

transSum exposes its tools over MCP, supporting both **stdio** (local subprocess) and **StreamableHTTP** (remote/web) transports.

### Transport

By default the server uses **stdio** transport (backward compatible with Claude Desktop). To enable remote access via HTTP, switch to **streamable-http**:

```bash
# Via CLI argument (takes precedence over env var)
uv run python -m transsum.mcp.server streamable-http

# Via environment variable
MCP_TRANSPORT=streamable-http uv run python -m transsum.mcp.server
```

When using StreamableHTTP, the server listens at `http://127.0.0.1:{MCP_SERVER_PORT}/mcp` (default port 8765).

**Client configuration examples:**

stdio (Claude Desktop):
```json
{
  "mcpServers": {
    "transsum": {
      "command": "uv",
      "args": [
        "--directory", "/absolute/path/to/transSum-server",
        "run", "python", "-m", "transsum.mcp.server"
      ]
    }
  }
}
```

StreamableHTTP (remote client):
```json
{
  "mcpServers": {
    "transsum": {
      "url": "http://127.0.0.1:8765/mcp"
    }
  }
}
```

Sampling and progress notifications work over both transports.

### MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `summarize_text` | `text` | Summarize a block of text with automatic chunking |
| `translate_text` | `text`, `target_language` (default: English) | Translate text into a target language |
| `summarize_file` | `file_path` | Load and summarize a document file (`.txt`, `.md`, `.html`, `.csv`, `.json`, `.pdf`) |

### MCP Resources

Resources let MCP clients read structured data from the server (config, capabilities, metadata) without the LLM deciding to call a tool. They are application-controlled, not model-controlled.

| Resource URI | MIME Type | Description |
|---|---|---|
| `transsum://config` | `application/json` | Current server configuration (API keys masked) |
| `transsum://supported-formats` | `application/json` | Supported file extensions grouped by category |
| `transsum://providers` | `application/json` | Available LLM providers with current settings |
| `transsum://config/{key}` | `text/plain` | Single config value by key (`provider`, `model`, `chunk_size`, `chunk_overlap`, `max_retries`, `timeout`) |

### MCP Notifications

The server emits real-time **progress** and **log message** notifications during long-running tool calls, so MCP clients (Claude Desktop, MCP Inspector) can display status updates.

- **Progress** (`notifications/progress`) — reports `(current_step, total_steps)` as chunks are processed
- **Log messages** (`notifications/message`) — descriptive status at each stage:
  - `"Document split into N chunks"` — after chunking
  - `"Processing single chunk..."` — fast-path start (single chunk)
  - `"Processed chunk i/N"` — after each MAP chunk completes
  - `"Merging N sections into final output..."` — before the REDUCE step
  - `"Complete"` — when processing finishes

Notifications are only emitted when running via MCP. The CLI and tests are unaffected.

### MCP Prompts

Prompts are reusable prompt templates that MCP clients can offer as slash commands or conversation starters. They guide the LLM to use transSum tools effectively.

| Prompt | Arguments | Description |
|--------|-----------|-------------|
| `summarize` | `text` | Summarize a block of text |
| `translate` | `text`, `language` (default: English) | Translate text into a target language |
| `summarize_from_file` | `file_path` | Load and summarize a document file |

### MCP Sampling

Sampling lets the MCP server ask the *client's* LLM to perform a task. transSum uses sampling to add a quality-review layer on summaries before returning them.

**How it works:**

1. After the pipeline produces a summary, the server sends it (along with a truncated excerpt of the source text) to the client's LLM via a sampling request.
2. The client's LLM evaluates the summary and responds with **PASS** or **FAIL** plus a brief explanation.
3. The result is included in the tool response as `quality_review` (`"pass"`, `"fail"`, or `"skipped"`) and an optional `quality_note` with the reviewer's reasoning.

**Which tools use it:**

- `summarize_text` — quality-checks the summary against the input text
- `summarize_file` — quality-checks the summary against the document content

**Graceful degradation:**

If the client does not support sampling, or the sampling request fails for any reason, the quality check is silently skipped and `quality_review` is set to `"skipped"`. The summary is still returned normally. CLI mode (no MCP context) also skips the quality check.

### MCP Roots

Roots let the MCP client declare which directories the server is allowed to access. When configured, `summarize_file` validates that the requested file path falls within one of the client's approved roots before loading it.

**How it works:**

1. Before loading a file, the server calls `list_roots()` to get the client's approved directory list.
2. Each root provides a `file://` URI pointing to an allowed directory.
3. The requested file path is resolved to an absolute path and checked against every root using `Path.relative_to()`.
4. If the file is under any root, access is allowed. Otherwise, a `ValueError` is raised listing the allowed directories.

**Which tools use it:**

- `summarize_file` — validates the file path against roots before loading

**Graceful degradation:**

If the client does not support roots, the `list_roots()` call fails, or no roots are declared, file access works as before with no restrictions. CLI mode (no MCP context) also skips the roots check.

### Test with MCP Inspector

The MCP Inspector is a browser-based tool for interacting with your server during development:

```bash
uv run mcp dev src/transsum/mcp/server.py
```

This opens an interactive UI where you can:
- **List Resources** — see all 4 entries (3 static + 1 template)
- **Read Resources** — fetch `transsum://config`, `transsum://supported-formats`, `transsum://providers`, or `transsum://config/chunk_size`
- **Call Tools** — invoke `summarize_text`, `translate_text`, or `summarize_file`
- **List & Invoke Prompts** — see all prompt templates and invoke them with arguments

### Run Standalone

```bash
uv run python -m transsum.mcp.server
```

### Register in Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "transsum": {
      "command": "uv",
      "args": [
        "--directory", "/absolute/path/to/transSum-server",
        "run", "python", "-m", "transsum.mcp.server"
      ]
    }
  }
}
```

Once registered, Claude Desktop can call `summarize_text`, `translate_text`, and `summarize_file` as tools during conversations.

## Architecture

```
User Input (CLI or MCP)
       │
       ▼
 DocumentLoader        ← Load from file or inline text
       │
       ▼
  TextChunker          ← Split into overlapping, sentence-aware chunks
       │
       ▼
ProcessingPipeline     ← Map-reduce: process chunks → merge results
       │
       ▼
 ModelAdapter          ← Ollama (HTTP) or Anthropic (SDK)
       │
       ▼
 Formatted Output      ← Rich panels (CLI) or JSON (MCP)
```

**Processing flow:**
1. **Load** — `DocumentLoader` reads the file or accepts inline text
2. **Chunk** — `TextChunker` splits long text at sentence boundaries with configurable overlap
3. **Map** — Each chunk is sent to the LLM with a task-specific prompt
4. **Reduce** — Partial results are merged into a single coherent output via a final LLM call
5. **Return** — CLI displays a Rich-formatted panel; MCP returns structured JSON

Short documents (single chunk) skip the map-reduce step and go through a fast path with one LLM call.

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_pipeline.py -v
```

Tests use mock adapters — no LLM calls are made during testing.

## Development

```bash
# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```
