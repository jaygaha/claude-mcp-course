# Introduction to MCP

A hands-on learning path for the **Model Context Protocol (MCP)** — the open standard that connects AI applications to external data sources, tools, and workflows through a unified interface.

This repository contains structured learning materials that progress from core concepts to a fully working CLI demo project (`cli_project_mcp`), covering server construction, client implementation, and the three MCP primitives: **Tools**, **Resources**, and **Prompts**.

---

## Table of Contents

- [Content Index](#content-index)
  - [1 — Introduction](#1--introduction)
  - [2 — Hands-on with MCP Servers](#2--hands-on-with-mcp-servers)
  - [3 — Connecting with MCP Clients](#3--connecting-with-mcp-clients)
- [Demo Project — documentMCP](#demo-project--documentmcp)
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

---

## Demo Project — documentMCP

The `cli_project_mcp` directory contains a complete, runnable demo that puts every concept from the learning materials into practice.

**What it does:** An interactive CLI chat application that connects Claude to an in-memory document store through MCP. Users can read, edit, summarize, and format documents via natural language, `@` mentions, and `/` commands.

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

See [`cli_project_mcp/README.md`](cli_project_mcp/README.md) for the full demo documentation.

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Anthropic API key** — obtain one at [console.anthropic.com](https://console.anthropic.com/)
- **uv** (recommended) — fast Python package manager ([github.com/astral-sh/uv](https://github.com/astral-sh/uv))

### Steps

```bash
# 1. Clone and enter the project
cd introduction-to-mcp/cli_project_mcp

# 2. Copy the environment template and add your API key
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY

# 3a. Install with uv (recommended)
pip install uv
uv venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
uv pip install -e .

# 3b. Or install with pip
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"
```

### Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `mcp[cli]` | Model Context Protocol SDK |
| `prompt-toolkit` | Interactive CLI with autocompletion |
| `python-dotenv` | `.env` file loading |

---

## Quick Start

```bash
# Run the CLI chat application
cd cli_project_mcp
uv run main.py            # or: python main.py
```

```
> What documents are available?          # plain chat
> Tell me about @deposition.md           # @mention injects document context
> /format spec.txt                       # /command runs a server-defined prompt
> /summarize report.pdf                  # Tab for autocompletion
```

To test the MCP server in isolation with the Inspector:

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
```

Follow the numbered sections in order. Each lesson builds on the previous one and culminates in the working `cli_project_mcp` demo.

## Course

- [Introduction on Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol)

