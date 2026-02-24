# documentMCP

A CLI-based chat application that demonstrates the **Model Context Protocol (MCP)** by integrating an MCP server and client with the Anthropic Claude API. The `documentMCP` demo project resides in the `cli_project_mcp` directory.

The application exposes an in-memory document store through MCP tools, resources, and prompts, allowing Claude to read, edit, summarize, and format documents on behalf of the user via an interactive terminal interface.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  CliApp (core/cli.py)                                    │
│  Interactive prompt with autocompletion for @docs, /cmds │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│  CliChat (core/cli_chat.py)                              │
│  Query processing, @mention extraction, /command routing │
└──────┬───────────────────────────────────┬───────────────┘
       │                                   │
┌──────▼──────────┐              ┌─────────▼──────────────┐
│ Claude API      │              │ MCPClient              │
│ (core/claude.py)│◄────────────►│ (mcp_client.py)        │
│ Tool-use loop   │  tool calls  │ stdio transport        │
└─────────────────┘              └─────────┬──────────────┘
                                           │ stdio
                                 ┌─────────▼──────────────┐
                                 │ MCP Server              │
                                 │ (mcp_server.py)         │
                                 │ Tools / Resources /     │
                                 │ Prompts                 │
                                 └─────────────────────────┘
```

## Features

- **MCP Tools** — `read_doc_contents` and `edit_doc_contents` let Claude read and modify documents through the agentic tool-use loop.
- **MCP Resources** — `docs://documents` lists available document IDs; `docs://documents/{doc_id}` returns individual document content.
- **MCP Prompts** — `/format` rewrites a document in Markdown; `/summarize` generates a concise summary.
- **`@` Mentions** — Reference documents inline (e.g., `@report.pdf`) to inject their content into the conversation context.
- **Smart Autocompletion** — Tab-completion for `/` commands, `@` resource mentions, and command arguments via `prompt_toolkit`.
- **Multi-Server Support** — Pass additional MCP server commands as arguments to `main.py` to connect multiple servers simultaneously.

## Project Structure

```
cli_project_mcp/
├── main.py              # Entry point — wires up Claude, MCP client, and CLI
├── mcp_server.py        # FastMCP server — tools, resources, prompts, document store
├── mcp_client.py        # MCP client — stdio connection and session management
├── core/
│   ├── chat.py          # Base chat class — agentic tool-use loop
│   ├── cli_chat.py      # CLI chat — @mention extraction, /command handling
│   ├── claude.py        # Anthropic API wrapper
│   ├── cli.py           # Interactive CLI with autocompletion and key bindings
│   └── tools.py         # Tool discovery and execution across MCP clients
├── pyproject.toml       # Project metadata and dependencies
├── .env.example         # Environment variable template
└── README.md
```

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

### 1. Configure environment variables

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY="sk-ant-..."
CLAUDE_MODEL="claude-sonnet-4-6"
USE_UV=1
```

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | **(required)** Anthropic secret key | — |
| `CLAUDE_MODEL` | Model ID passed to the API | `claude-sonnet-4-6` |
| `USE_UV` | Set to `1` when using `uv`, `0` otherwise | `1` |

### 2. Install dependencies

#### Option A — with uv (recommended)

```bash
pip install uv          # install uv if needed
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Option B — with pip

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"
```

### 3. Run the application

```bash
# with uv
uv run main.py

# without uv
python main.py
```

## Usage

### Chat

Type a message and press **Enter** to chat with Claude:

```
> What can you help me with?
```

### Reference documents with `@`

Prefix a document ID with `@` to include its content in the query:

```
> Summarize the key points in @deposition.md
> Compare @financials.docx with @outlook.pdf
```

### Run commands with `/`

Execute server-defined prompts using the `/` prefix:

```
> /format spec.txt
> /summarize report.pdf
```

Press **Tab** at any point to trigger autocompletion for commands, documents, and arguments.

### Test the MCP server independently

Use the MCP Inspector to interact with the server outside the CLI:

```bash
mcp dev mcp_server.py
```

## Development

### Adding documents

Add entries to the `docs` dictionary in `mcp_server.py`:

```python
docs["my_doc.md"] = "# New Document\nContent goes here."
```

### Adding tools

Define a new function decorated with `@mcp.tool()` in `mcp_server.py`. The tool is automatically discovered by the client and made available to Claude.

### Adding prompts

Define a new function decorated with `@mcp.prompt()` in `mcp_server.py`. Prompts appear as `/` commands in the CLI.

### Connecting additional MCP servers

Pass extra server commands as arguments to `main.py`:

```bash
uv run main.py "uv run other_server.py"
```

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `mcp[cli]` | Model Context Protocol SDK |
| `prompt-toolkit` | Interactive CLI with autocompletion |
| `python-dotenv` | `.env` file loading |

## License

This project is provided for educational purposes as part of an introduction to the Model Context Protocol.
