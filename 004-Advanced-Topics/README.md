# Advanced Topics

Deep dives into MCP features beyond the three core primitives (Tools, Resources, Prompts). Each topic includes a standalone lesson and a runnable demo application.

## Lessons

| # | File | Topic | Summary |
|---|------|-------|---------|
| 4.1 | [Sampling](001-Core-MCP-features.md) | Sampling | The "reverse request" — how servers ask clients to generate text via the LLM. Security, cost, and the stdio vs. HTTP trade-offs. |
| 4.2 | [Log and Progress Notifications](002-Log-and-progress-notifications.md) | Notifications | Real-time feedback during tool execution using `ctx.info()` and `ctx.report_progress()`. Server-side and client-side setup. |
| 4.3 | [Roots](003-Roots.md) | Roots | Scoped file system access — granting servers permission to specific directories and enforcing boundaries with `is_path_allowed()`. |
| 4.4 | [JSON Message Types](004-JSON-message-types.md) | Messages & Transports | The JSON-RPC message format (requests, results, notifications), transport types (stdio, Streamable HTTP), and critical server flags. |
| 4.5 | [The STDIO Transport](005-The-STDIO-transport.md) | Stdio | How stdio works — bidirectional communication, the initialization handshake, and the same-machine limitation. |
| 4.6 | [The StreamableHTTP Transport](006-The-StreamableHTTP-transport.md) | HTTP | Hosting MCP servers remotely — SSE for bidirectional messaging, session IDs, and the `stateless`/`json_response` danger flags. |

## Demo Applications

Each demo is a standalone project with its own `pyproject.toml` and setup instructions.

| Demo | Directory | What it Demonstrates |
|------|-----------|----------------------|
| **Sampling** | [`sampling/`](sampling/) | Server requests LLM text generation from the client via a sampling callback. |
| **Notifications** | [`notifications/`](notifications/) | Server sends real-time log messages and progress updates during tool execution. |
| **Roots** | [`roots/`](roots/) | CLI chat with scoped file system access and video conversion using FFmpeg. |
| **StreamableHTTP** | [`transport-http/`](transport-http/) | Browser-based MCP protocol explorer showing the JSON-RPC handshake over HTTP. |

## Prerequisites

All demos require **Python 3.10+** and **uv**. Demos that call Claude also require an `ANTHROPIC_API_KEY` (see each demo's `.env.example`).
