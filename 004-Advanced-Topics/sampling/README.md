# MCP Sampling Demo

A demonstration of **Sampling** in MCP — where the Server asks the Client to generate text using an LLM, reversing the normal request direction.

## Setup

1. Copy `.env.example` to `.env` and set your `ANTHROPIC_API_KEY`.
2. Install dependencies:

```bash
uv sync
```

## Running the Demo

```bash
uv run client.py
```

The client connects to the server via stdio. The server's `summarize` tool triggers a sampling request back to the client, which forwards the prompt to Claude and returns the generated text.

---

# MCP Sampling

## 1. What is "Sampling"?
Usually, the **Client** (the user/app) asks the **Server** (the tool) to do work.
**Sampling** flips this script. It is a technique where the **Server asks the Client** to use the AI (LLM) to generate text.

### The Analogy
Imagine you hire a specialized accountant (The Server). They are great at math but bad at writing emails.
*   **Normal:** You ask the accountant to calculate taxes.
*   **Sampling:** The accountant stops and asks *you*: "Hey, I calculated the numbers, but can you write the polite email to the IRS for me? You are better at writing."

## 2. Why do we need it?
The main reason is **Money and Security**.
*   **No API Keys on Server:** If you build a public MCP Server, you don't want to put your own expensive API key inside it.
*   **User Pays:** Sampling forces the **Client** (the user) to use their own API key and quota.
*   **Privacy:** It prevents strangers from using your server to generate free AI text.

## 3. The Walkthrough: Step-by-Step
Here is the lifecycle of a sampling request, which looks like a "relay race":

1.  **Server Start:** The Server is running a tool but realizes it needs "intelligence" (e.g., to summarize a file).
2.  **The Request:** The Server calls `create_message()` with a list of messages (prompts).
3.  **The Handoff:** The Client receives this request via a **Sampling Callback**.
4.  **The Brain:** The Client sends the prompt to the actual LLM (Claude).
5.  **The Return:** The Client gets the text back from Claude and sends it *back* to the Server.
6.  **The Finish:** The Server uses that generated text to finish its original job.

## 4. How to Implement It

### A. On the Server Side (The Asker)
You don't need to install an LLM. You just use the MCP function:
*   **Command:** `create_message()`
*   **Input:** You send a list of messages (just like you would send to a chatbot).

### B. On the Client Side (The Helper)
The Client must be listening for these requests.
*   **Callback:** You must write a specific function (a "Sampling Callback") that says: *"If the server asks for help, I will talk to Claude and give the answer back"*.

## 5. The "Danger Zone": HTTP & Statelessness
This is the most critical technical detail to remember. Sampling relies on **Server-to-Client** communication.

*   **Local (Stdio):** Works perfectly. The line is open both ways.
*   **Streamable HTTP:** Can work, but requires a complex setup using "Server-Sent Events" (SSE) to keep a channel open.
*   **Stateless HTTP (The Trap):** If you turn on **Stateless Mode** (`stateless=true`) to make your server faster or handle more users, **Sampling stops working**.
    *   *Why?* In stateless mode, the server forgets who the client is immediately after replying. It cannot "call them back" to ask for sampling.

**Beginner Tip:** If you are building a tool that uses Sampling, test it locally first. If you deploy it to the web, make sure you **do not** enable "Stateless" or "JSON Response" modes, or the feature will break.

***
