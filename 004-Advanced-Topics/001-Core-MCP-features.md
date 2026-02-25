# Sampling in MCP

## 1. The Concept: "The Reverse Request"
Normally, the Client (Claude) asks the Server to do work (like "Add these numbers" or "Read this file").

**Sampling** flips this around. It is a technique where the **Server asks the Client** to generate text using the Language Model (LLM).

### The Analogy

Imagine the MCP Server is a specialized worker (like a Calculator). It is good at math, but it cannot write poetry or summarize text.

*   **Without Sampling:** The Server hits a wall if it needs to summarize data.
*   **With Sampling:** The Server pauses and asks the Client: *"Hey, you have access to the big brain (Claude). Can you write this summary for me?"*

## 2. Why use it? (The "Who Pays?" Problem)

The main reason to use sampling is **Security and Cost**.

*   **No API Keys on Server:** If you build a public MCP Server, you don't want to put your own secret API keys inside it. If you did, you would pay for every user's request.
*   **Shift Responsibility:** Sampling forces the **Client** (the user) to use their own API key and quota.
*   **Privacy:** It prevents unauthorized usage of tokens on public servers.

## 3. How the Architecture Works
The process works like a relay race:

1.  **Server Request:** The Server realizes it needs LLM help. It uses a function called `create_message()` containing the prompt.
2.  **Handoff:** The Client receives this request via a "Sampling Callback."
3.  **The Brain:** The Client sends the prompt to the LLM (Claude).
4.  **Return:** The Client gets the text back from Claude and sends it *back* to the Server.
5.  **Finish:** The Server uses that text to finish its job.

## 4. Implementation Basics

### On the Server Side
You don't need to install an LLM. You just use the MCP SDK to send a message.
*   **Function:** `create_message()`
*   **Input:** You send a list of messages (just like you would send to a chatbot).

### On the Client Side
The Client must be listening for these requests.
*   **Callback:** The Client must implement a "Sampling Callback." This is a function that says, *"If the server asks for a completion, I will handle it and return the result"*.

## 5. Important Warning: The "HTTP" Trap
Sampling is a **Server-to-Client** request (the Server is starting the conversation). This causes problems if you are connecting over the web (HTTP) instead of running locally on your computer.

*   **Stdio (Local):** Works perfectly. The line is open both ways.
*   **Standard HTTP:** By default, HTTP is one-way (Client calls Server). It is very hard for the Server to "call" the Client.
*   **The Killer Flag:** If you set **Stateless HTTP** to `true` (often used for scaling servers), it **disables sampling** entirely because the server loses the ability to track who the client is.

**Beginner Tip:** If you are building a Server that uses Sampling, test it locally (Stdio) first. If you deploy it to the web, you must ensure your transport allows "Server-initiated requests".

***