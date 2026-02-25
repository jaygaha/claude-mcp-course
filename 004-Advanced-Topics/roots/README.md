# MCP Roots Demo

A CLI chat application demonstrating **Roots** in MCP — secure, scoped file system access for MCP servers.

The client passes user-specified root directories to the server. The server can only access files within those roots, enforced by an `is_path_allowed()` check. Tools include directory listing (`read_dir`), root listing (`list_roots`), and video conversion (`convert_video`) using FFmpeg.

## Prerequisites

- Python 3.10+
- Anthropic API Key
- FFmpeg (for video conversion features)

To install FFmpeg on macOS:

```bash
brew install ffmpeg
```

## Setup

1. Copy `.env.example` to `.env` and set your `ANTHROPIC_API_KEY`.
2. Install dependencies:

```bash
uv sync
```

## Running the Demo

You must specify one or more root directories that the MCP server will have access to:

```bash
# Single directory
uv run main.py /path/to/videos

# Multiple directories
uv run main.py /home/user/videos /mnt/storage/media ~/Documents

# Current directory
uv run main.py .
```

## Available Tools

| Tool | Description |
|---|---|
| `list_roots` | List all accessible root directories |
| `read_dir` | Read contents of a directory (must be within a root) |
| `convert_video` | Convert MP4 videos to other formats (avi, mov, webm, mkv, gif) |

## How Roots Work

1. The user passes directory paths as command-line arguments.
2. The client converts them to `Root` objects with `file://` URIs.
3. When the server needs to access a file, it calls `list_roots()` via the client callback.
4. The server's `is_path_allowed()` function validates the requested path is within an authorized root.
5. Access outside roots is denied — this is a security boundary the developer must enforce manually.
