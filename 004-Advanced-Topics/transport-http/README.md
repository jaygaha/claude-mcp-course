# MCP StreamableHTTP Transport Demo

A browser-based demonstration of the **StreamableHTTP transport** — the mechanism for hosting MCP servers remotely over HTTP.

The server exposes an `add` tool over Streamable HTTP and serves an interactive HTML page at `http://localhost:8000/`. The page walks through the MCP handshake step by step: Initialize, Initialized Notification, and Tool Call, showing the raw JSON-RPC requests and responses exchanged over HTTP.

## Important Note

This demo runs with `stateless_http=True` and `json_response=True`. These flags are set **intentionally** to show what happens when stateless mode is enabled:

- No session IDs are assigned
- No Server-Sent Events (SSE) streaming
- No intermediate progress or log notifications
- The server responds with a single JSON blob only after the tool finishes

To see full bidirectional features (progress, logging, SSE), set both flags to `False`.

## Setup

Install dependencies:

```bash
uv sync
```

## Running the Demo

Start the server:

```bash
uv run main.py
```

Then open `http://localhost:8000/` in a browser and click through the three steps to observe the MCP protocol in action.

## What the Demo Shows

| Step | JSON-RPC Method | What Happens |
|---|---|---|
| 1. Initialize | `initialize` | Client sends capabilities, server responds with its own. Session ID assigned (if stateful). |
| 2. Initialized | `notifications/initialized` | Client confirms readiness. Server responds `202 Accepted`. |
| 3. Tool Call | `tools/call` | Client invokes `add(5, 3)`. Server returns the result. |

The SSE panel on the bottom-right monitors server-initiated events (only active when `stateless_http=False`).
