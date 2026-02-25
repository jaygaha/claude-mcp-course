# MCP Notifications Demo

A demonstration of **Log and Progress Notifications** in MCP — real-time feedback from server to client during long-running tool execution.

The server's `add` tool sends `ctx.info()` log messages and `ctx.report_progress()` updates while it runs. The client listens via logging and progress callbacks and prints updates to the terminal.

## Setup

Install dependencies:

```bash
uv sync
```

## Running the Demo

```bash
uv run client.py
```

You will see log messages and progress percentages printed in real time before the final result.

---

# Beginner Notes: Notification Walkthrough

## 1. What are Notifications?
Imagine ordering a pizza and watching the tracker: *"Preparing"* → *"Baking"* → *"Out for delivery."*

**Notifications** are the MCP equivalent of that tracker.
*   **The Problem:** Without them, when an AI runs a slow tool (like "Scan Database"), the chat just hangs. The user wonders, "Is it broken? Did it crash?".
*   **The Solution:** These features allow the Server to send real-time updates back to the Client so the user sees exactly what is happening.

## 2. The Two Types of Feedback
MCP Servers can send two specific types of updates to the user:

### A. Logging (`info`)
*   **What it is:** Text-based updates, similar to "print statements" in code.
*   **Use Case:** Telling the user "Connected to database..." or "Found 5 files...".

### B. Progress (`report_progress`)
*   **What it is:** Numeric updates, usually 0 to 100.
*   **Use Case:** Driving a progress bar on the user's screen (e.g., "50% complete").

## 3. The Walkthrough: How it Flows
Here is the step-by-step lifecycle of a notification:

1.  **Start:** The Client (Claude) asks the Server to run a tool.
2.  **Context:** The MCP system automatically gives the tool a special helper called the **`context` object**.
3.  **Action:** Inside the tool's code, the developer calls `ctx.info("Working...")` or `ctx.report_progress(50)`.
4.  **Transmission:** The Server immediately shoots this message back to the Client *while the tool is still running*.
5.  **Display:** The Client's "Callback functions" catch this message and show it to the user (e.g., updating a text log or a visual bar).

## 4. Implementation Basics

### On the Server Side (The Sender)
You don't need complex code. You just use the `context` argument.
*   **Logs:** Call `ctx.info('message')`.
*   **Progress:** Call `ctx.report_progress(percentage)`.

### On the Client Side (The Receiver)
Your Client application needs "ears" to listen for these updates.
*   **Log Callback:** You attach this to the **Client Session**. It handles general messages.
*   **Progress Callback:** You attach this specifically to the **`call_tool`** function. It handles updates for that specific task.

## 5. Critical Warning: The "HTTP Trap"
This is the most important technical detail for beginners.

Notifications are **Server-to-Client** messages. This creates a challenge depending on how you connect:

*   **Local (Stdio):** Works perfectly. The connection is a two-way street.
*   **Streamable HTTP:** Works, but relies on a technology called **SSE (Server-Sent Events)** to keep a channel open for the server to talk back.
*   **The "Stateless" Switch:** If you turn on **Stateless Mode** (`stateless=true`) or **JSON Response** (`json_response=true`) to make your server faster, **it breaks notifications entirely**.
    *   *Why?* In these modes, the server forgets the client immediately. It cannot "call back" to say "I'm 50% done." The client will only hear back when the job is 100% finished.

**Beginner Tip:** If you want progress bars, do **not** use "Stateless HTTP."

***