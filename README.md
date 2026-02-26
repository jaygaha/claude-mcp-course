# Introduction to MCP

A hands-on learning path for the **Model Context Protocol (MCP)** — the open standard that connects AI applications to external data sources, tools, and workflows through a unified interface.

This repository contains structured learning materials that progress from core concepts to working demo projects, covering server construction, client implementation, the three MCP primitives (**Tools**, **Resources**, **Prompts**), and advanced topics like sampling, notifications, roots, and transports.

---

## Table of Contents

- [Content Index](#content-index)
  - [1 — Introduction](#1--introduction)
  - [2 — Hands-on with MCP Servers](#2--hands-on-with-mcp-servers)
  - [3 — Connecting with MCP Clients](#3--connecting-with-mcp-clients)
  - [4 — Advanced Topics](#4--advanced-topics)
- [Demo Projects](#demo-projects)
  - [documentMCP](#documentmcp--cli_project_mcp)
  - [Sampling](#sampling--004-advanced-topicssampling)
  - [Notifications](#notifications--004-advanced-topicsnotifications)
  - [Roots](#roots--004-advanced-topicsroots)
  - [StreamableHTTP](#streamablehttp--004-advanced-topicstransport-http)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [MCP Primitives at a Glance](#mcp-primitives-at-a-glance)

---

## Content Index

### 1 — Introduction

Foundational concepts behind MCP and the role of clients in the protocol.

| # | File | Summary |
|---|------|---------|
| 1.1 | [Introducing MCP](001-Introduction/001-Introducing-MCP.md) | What MCP is, the USB-C analogy, client/server architecture, capabilities overview, and real-world use cases. |
| 1.2 | [MCP Clients](001-Introduction/002-MCP-clients.md) | The client as intermediary between AI models and servers — tool management, resource access, prompt handling, and the full interaction workflow loop. |

### 2 — Hands-on with MCP Servers

Build and test an MCP server from scratch using the Python SDK and FastMCP.

| # | File | Summary |
|---|------|---------|
| 2.1 | [Project Setup](002-Hands-on-with-MCP-Servers/001-Project-setup.md) | Setting up a Python environment, transport options (stdio), session management, and dependency installation. |
| 2.2 | [Define Tools in MCP](002-Hands-on-with-MCP-Servers/002-Define-tools-in-MCP.md) | Creating tools with the `@mcp.tool` decorator, type hints, pydantic `Field` validation, error handling, and real-world examples (`read_doc_contents`, `edit_document`). |
| 2.3 | [The Server Inspector](002-Hands-on-with-MCP-Servers/003-The-server-inspector.md) | Using the MCP Inspector (`mcp dev`) to test servers interactively without building a full client. |

### 3 — Connecting with MCP Clients

Implement a client that connects to MCP servers and integrates with Claude.

| # | File | Summary |
|---|------|---------|
| 3.1 | [Implementing a Client](003-Connecting-with-MCP-clients/001-Implementing-a-client.md) | Building a class-based MCP client — session lifecycle, async context management, tool/resource/prompt wrappers, and the complete data flow. |
| 3.2 | [Defining Resources](003-Connecting-with-MCP-clients/002-Defining-resources.md) | Server-side resource definitions — static vs. templated URIs, the `@mcp.resource` decorator, URI design, and MIME types. |
| 3.3 | [Accessing Resources](003-Connecting-with-MCP-clients/003-Accessing-resources.md) | Client-side resource reading — `read_resource` implementation, `AnyUrl` wrapping, and MIME-based content parsing. |
| 3.4 | [Defining Prompts](003-Connecting-with-MCP-clients/004-Defining-prompts.md) | Server-side prompt templates — the `@mcp.prompt` decorator, argument injection, `UserMessage` construction, and use cases. |
| 3.5 | [Prompts in the Client](003-Connecting-with-MCP-clients/005-Prompts-in-the-client.md) | Client-side prompt consumption — `list_prompts` for discovery, `get_prompt` for retrieval, and the end-to-end prompt workflow. |
| 3.6 | [MCP Review](003-Connecting-with-MCP-clients/006-MCP-review.md) | Cheat-sheet covering the three primitives, a decision matrix for choosing between them, and the full development lifecycle. |

### 4 — Advanced Topics

Deep dives into MCP features beyond the three core primitives.

| # | File | Summary |
|---|------|---------|
| 4.1 | [Sampling](004-Advanced-Topics/001-Core-MCP-features.md) | The "reverse request" — servers ask clients to generate text via the LLM. Security, cost, and stdio vs. HTTP trade-offs. |
| 4.2 | [Log and Progress Notifications](004-Advanced-Topics/002-Log-and-progress-notifications.md) | Real-time feedback during tool execution using `ctx.info()` and `ctx.report_progress()`. Server and client setup. |
| 4.3 | [Roots](004-Advanced-Topics/003-Roots.md) | Scoped file system access — granting servers permission to specific directories, autonomous discovery, and enforcing boundaries. |
| 4.4 | [JSON Message Types](004-Advanced-Topics/004-JSON-message-types.md) | The JSON-RPC message format (requests, results, notifications), transport comparison, and critical server flags (`stateless`, `json_response`). |
| 4.5 | [The STDIO Transport](004-Advanced-Topics/005-The-STDIO-transport.md) | How stdio works — bidirectional communication via stdin/stdout, the initialization handshake, and the same-machine limitation. |
| 4.6 | [The StreamableHTTP Transport](004-Advanced-Topics/006-The-StreamableHTTP-transport.md) | Hosting MCP servers remotely — Server-Sent Events (SSE) for bidirectional messaging, session IDs, and danger flags. |

See [`004-Advanced-Topics/README.md`](004-Advanced-Topics/README.md) for the full section index including demo applications.

---

## Demo Projects

### documentMCP — `cli_project_mcp/`

The primary demo application. An interactive CLI chat that connects Claude to an in-memory document store through MCP. Supports `@` document mentions, `/` commands, and tab autocompletion.

```
cli_project_mcp/
├── main.py              # Entry point
├── mcp_server.py        # FastMCP server — tools, resources, prompts
├── mcp_client.py        # MCP client — stdio transport
├── core/
│   ├── chat.py          # Base chat class — agentic tool-use loop
│   ├── cli_chat.py      # @mention extraction, /command routing
│   ├── claude.py        # Anthropic API wrapper
│   ├── cli.py           # Interactive CLI with autocompletion
│   └── tools.py         # Tool discovery and execution
├── pyproject.toml       # Dependencies
└── .env.example         # Environment variable template
```

See [`cli_project_mcp/README.md`](cli_project_mcp/README.md) for full documentation.

## Advanced-Topics

### Sampling — `004-Advanced-Topics/sampling/`

Demonstrates the **reverse request** pattern. The server's `summarize` tool asks the client to call Claude via a sampling callback, so the server never needs its own API key.

See [`004-Advanced-Topics/sampling/README.md`](004-Advanced-Topics/sampling/README.md).

### Notifications — `004-Advanced-Topics/notifications/`

Demonstrates **real-time feedback**. The server's `add` tool sends log messages (`ctx.info()`) and progress updates (`ctx.report_progress()`) to the client during execution.

See [`004-Advanced-Topics/notifications/README.md`](004-Advanced-Topics/notifications/README.md).

### Roots — `004-Advanced-Topics/roots/`

Demonstrates **scoped file system access**. A CLI chat where the user passes root directories as arguments. The server can only access files within those roots, enforced by `is_path_allowed()`. Includes a video converter tool using FFmpeg.

See [`004-Advanced-Topics/roots/README.md`](004-Advanced-Topics/roots/README.md).

### StreamableHTTP — `004-Advanced-Topics/transport-http/`

Demonstrates the **HTTP transport** with a browser-based protocol explorer. Walks through the JSON-RPC handshake (Initialize, Initialized, Tool Call) and shows raw request/response payloads. Runs with `stateless_http=True` to illustrate the limitations of stateless mode.

See [`004-Advanced-Topics/transport-http/README.md`](004-Advanced-Topics/transport-http/README.md).

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Anthropic API key** — obtain one at [console.anthropic.com](https://console.anthropic.com/)
- **uv** (recommended) — fast Python package manager ([github.com/astral-sh/uv](https://github.com/astral-sh/uv))
- **FFmpeg** — required only for the Roots demo video conversion feature

### documentMCP (main demo)

```bash
cd introduction-to-mcp/cli_project_mcp

# Configure environment
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY

# Install with uv (recommended)
pip install uv
uv venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
uv pip install -e .

# Or install with pip
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"
```

### Advanced topic demos

Each demo in `004-Advanced-Topics/` is self-contained:

```bash
cd 004-Advanced-Topics/<demo-directory>

# Configure environment (where applicable)
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY

# Install and run
uv sync
uv run client.py       # sampling, notifications
uv run main.py         # roots, transport-http
```

### Dependencies

| Package | Used by | Purpose |
|---|---|---|
| `anthropic` | documentMCP, sampling, roots | Claude API client |
| `mcp[cli]` | All projects | Model Context Protocol SDK |
| `prompt-toolkit` | documentMCP, roots | Interactive CLI with autocompletion |
| `python-dotenv` | documentMCP, roots | `.env` file loading |
| `aioconsole` | sampling, notifications | Async console I/O |

---

## Quick Start

```bash
# Run the main CLI chat application
cd cli_project_mcp
uv run main.py            # or: python main.py
```

```
> What documents are available?          # plain chat
> Tell me about @deposition.md           # @mention injects document context
> /format spec.txt                       # /command runs a server-defined prompt
> /summarize report.pdf                  # Tab for autocompletion
```

To test an MCP server in isolation with the Inspector:

```bash
mcp dev mcp_server.py
```

---

## MCP Primitives at a Glance

| Primitive | Controlled by | Purpose | Example |
|---|---|---|---|
| **Tools** | AI model | Perform actions | `read_doc_contents`, `edit_doc_contents` |
| **Resources** | Application | Expose data | `docs://documents`, `docs://documents/{id}` |
| **Prompts** | User | Start workflows | `/format`, `/summarize` |

---

## Recommended Learning Path

```
Introducing MCP ➜ MCP Clients ➜ Project Setup ➜ Define Tools ➜ Server Inspector
    ➜ Implementing a Client ➜ Resources ➜ Prompts ➜ MCP Review ➜ Run the Demo
    ➜ Sampling ➜ Notifications ➜ Roots ➜ Transports ➜ Run Advanced Demos
```

Follow the numbered sections in order. Sections 1-3 build toward the `cli_project_mcp` demo. Section 4 explores advanced features with standalone demos.

## Course

- [Introduction on Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [Model Context Protocol: Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [Introduction to agent skills
](https://anthropic.skilljar.com/introduction-to-agent-skills)
  - [Course Path](./010-Introduction-to-agent-skills/README.md)