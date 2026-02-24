# How to Setup an MCP Client

## 1. The Concept: What are we building?
When you build an **MCP Client**, you are building a "wrapper" or a "bridge."
*   **The Goal:** Connect your application (like a chatbot) to an MCP Server (where the tools live).
*   **The Role:** The Client does not run the tools itself. It acts as a messenger that sends requests to the server and gets results back.

## 2. Key Requirements
To set up a client, you need to understand three technical components described in the documentation:

*   **Transport:** This is *how* the client talks to the server. The most common setup for beginners is **Stdio** (Standard Input/Output), where the client and server run on the same machine.
*   **Session:** The active connection line. You must open a session to talk, and close it when done.
*   **Dependencies:** You will typically use the MCP Python SDK, which requires libraries like `json` and `pydantic` (specifically `AnyUrl` for handling addresses).

## 3. Step-by-Step Implementation

### Step A: Initialize the Connection (The Session)
Your client code acts as a wrapper around a `ClientSession`.
*   **Pattern:** You don't just open a connection; you must manage its lifecycle.
*   **Cleanup is Critical:** When your application shuts down, the client **must** close the connection properly. The SDK handles this using "async enter/exit" functions. Think of it like hanging up the phone—you don't want to leave the line open forever,.

### Step B: Implement Tool Capabilities
The most common use of a client is to let an AI use tools (like a calculator or database).
1.  **List Tools:** Your client needs a function (e.g., `list_tools()`) that sends a request to the server asking, "What can you do?"
    *   *Code action:* `await self.session.list_tools()`.
2.  **Call Tools:** When the AI wants to use a tool, your client sends the command.
    *   *Code action:* `await self.session.call_tool(name, arguments)`.

### Step C: Implement Resource Capabilities
If you want your AI to read files or data directly:
1.  **Read Resource:** You need a function that takes a URI (a link like `file:///report.pdf`) and asks the server for the content.
    *   *Code action:* `await self.session.read_resource(AnyUrl(uri))`.
2.  **Parse the Result:** The server might send back JSON or plain text. Your client should check the `mime_type` to decide how to read it (e.g., using `json.loads` if it is application/json).

### Step D: Implement Prompt Capabilities
If you want to use pre-written templates (Prompts) from the server:
1.  **List Prompts:** Ask the server what templates are available.
    *   *Code action:* `await self.session.list_prompts()`.
2.  **Get Prompt:** Ask the server to fill out a specific template with arguments (like a document ID).
    *   *Code action:* `await self.session.get_prompt(name, arguments)`.

## 4. The "flow" of a Client
When you put it all together, your Client setup handles this specific loop:

1.  **Discovery:** The App asks the Client, "Get me the tools." The Client asks the Server.
2.  **Selection:** The AI (Claude) picks a tool.
3.  **Execution:** The Client sends the `call_tool` command to the Server.
4.  **Result:** The Server sends the data back to the Client.
5.  **Handoff:** The Client gives the data to the AI.

## 5. Tips for Beginners
*   **Don't reinvent the wheel:** Use the Python SDK. It handles the messy parts of the communication protocol for you.
*   **Testing:** You can run your client script (`python client.py`) with a simple test harness to make sure it connects and lists tools before you try to hook it up to a complex AI.
*   **Learning Project:** If you are studying, try building a "CLI Chatbot." This allows you to build a Client and Server in the same project to see how they talk to each other without needing external API keys immediately.
