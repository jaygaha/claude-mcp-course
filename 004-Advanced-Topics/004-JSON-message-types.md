
# MCP Communication: Messages & Transports

## 1. JSON Message Types (The Language)
MCP uses **JSON** (JavaScript Object Notation) as its universal language. Every time a Client and Server talk, they are swapping JSON objects.

### The Two Main Categories
There are two distinct ways these messages behave:

1.  **Requests & Results (The Conversation)**
    *   **How it works:** Like a phone call. You ask a question, you wait, you get an answer.
    *   **Rule:** They always come in pairs.
    *   **Example:** `call_tool_request` (Do this) + `call_tool_result` (Here is the data).

2.  **Notifications (The "FYI")**
    *   **How it works:** Like a text message or a shout. You send it, but you don't expect a reply.
    *   **Rule:** One-way only.
    *   **Example:** `progress_notification` (I'm 50% done) or `logging_message` (Connected to DB).

### The Direction Problem
It is crucial to understand *who* is talking.
*   **Client Messages:** Sent by the App (Claude) to the Server.
*   **Server Messages:** Sent by the Server to the App.

**Why this matters:** Some features (like Sampling, Progress Bars, and Logging) require the **Server to talk to the Client**. As you will see below, some connection methods make this very difficult.

***

## 2. Transports (The "Highway")
A **Transport** is the mechanism used to move these JSON messages back and forth. Think of it as the physical wire or connection type.

### A. Stdio Transport (The "Local Cable")
This is the default for running things on your own computer.
*   **How it works:** The Client launches the Server as a sub-process and they talk via "Standard Input/Output" (typing and reading text streams).
*   **The Superpower:** It is **Bidirectional**. The Client can talk, and the Server can talk whenever it wants.
*   **Pros:** Supports everything (Sampling, Progress, Logging).
*   **Cons:** The Client and Server must be on the **same physical machine**.

### B. Streamable HTTP (The "Web Connection")
This is used when you want to host a server on the internet (e.g., at `mcpserver.com`).
*   **The Problem:** Standard HTTP is a one-way street. Clients can easily request things, but Servers cannot easily "call" the Client back.
*   **The Workaround (SSE):** To fix this, MCP uses **Server-Sent Events (SSE)**.
    *   The Client opens a long-lived connection just to listen for updates.
    *   This allows the Server to stream messages (like "I need you to sample this text") back to the Client.

***

## 3. Critical Settings: The "Danger Zone"
If you use HTTP, there are two settings (flags) that can break your features. Beginners often trip over these when trying to make their servers faster ("scaling").

### Flag 1: Stateless HTTP (`stateless=true`)
Used when you have thousands of users and multiple server copies.
*   **What it does:** The Server forgets who the Client is immediately after replying. No Session IDs are assigned.
*   **The Cost:** It **kills Server-to-Client features**.
    *   ❌ No Sampling (Server can't ask Client for help).
    *   ❌ No Progress Bars (Server can't send updates).
    *   ❌ No Logs.
*   **Why?** The Server cannot track the "listening" line (SSE) to send messages back.

### Flag 2: JSON Response (`json_response=true`)
Used to simplify the data.
*   **What it does:** It disables "Streaming." The Server waits until the job is 100% done, then sends one big JSON blob.
*   **The Cost:**
    *   ❌ No intermediate updates.
    *   ❌ No "50% complete" messages.
    *   You just wait in silence until the tool finishes.

## 4. Summary Checklist for Beginners
*   **Local Development:** Use **Stdio**. It is the easiest and supports all features (Sampling, Logs, Progress).
*   **Remote Deployment:** Use **Streamable HTTP** with SSE enabled.
*   **Troubleshooting:** If your Progress Bars or Sampling stop working on the web, check if you accidentally turned on **Stateless Mode**.

***