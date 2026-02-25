# Log and Progress Notifications

## 1. What are they?
Imagine ordering a pizza and watching the tracker: *"Preparing" → "Baking" → "Out for delivery."*

**Log and Progress Notifications** are the MCP equivalent of that tracker.
*   **The Problem:** Without them, when an AI runs a slow tool (like "Scan Database"), the chat just hangs. The user wonders, "Is it broken? Did it crash?".
*   **The Solution:** These features allow the Server to send real-time updates back to the Client so the user sees what is happening.

## 2. Server-Side Setup (The Sender)
To make your tools send updates, you don't need complex code. You just need to use the **Context** object.

### Step A: Accept the "Context"
When you write a tool function, the MCP system automatically provides a special argument called `context`. It is usually passed as the **last parameter** of your function.

### Step B: Send the Updates
Inside your tool logic, you can call two specific methods on that context object:

1.  **`info()`**: Used for general logging (like print statements).
    *   *Example:* `ctx.info("Connected to database...")`
2.  **`report_progress()`**: Used for status bars.
    *   *Example:* `ctx.report_progress(50)` (to show 50% complete).

**Result:** Calling these automatically shoots a message back to the Client immediately, even if the tool hasn't finished running yet.

## 3. Client-Side Setup (The Receiver)
Your Client application needs "ears" to listen for these updates. You do this using **Callbacks** (functions that run when a message arrives).

### A. Handling Logs
*   **Where it goes:** You pass a logging callback to the **Client Session** itself.
*   **What it does:** Whenever the server says `ctx.info()`, this function runs. You might make it print text to the terminal or save it to a debug file.

### B. Handling Progress
*   **Where it goes:** You pass a progress callback specifically to the **`call_tool`** function.
*   **What it does:** Whenever the server says `ctx.report_progress()`, this function runs. You might use it to update a loading bar on a website.

## 4. The "HTTP Trap" (Warning for Beginners)
This is the most critical technical detail to remember.

These notifications are **Server-to-Client** messages.
*   **Local (Stdio):** If you run MCP locally, this works perfectly because the connection is two-way.
*   **Remote (HTTP):** If you host your server on the web, standard HTTP is one-way (Client talks to Server). It is very hard for the Server to "push" a progress update back to the Client.

**The "Stateless" Switch:**
If you configure your HTTP server with `stateless=true` or `json_response=true` (often done for scaling), **it breaks progress and logging entirely**. The server loses the ability to send these intermediate updates, and the client will only hear back when the tool is 100% finished.

## 5. Summary Checklist
*   [ ] **Server:** Ensure your tool accepts the `context` argument.
*   [ ] **Server:** Use `ctx.info()` for text logs.
*   [ ] **Server:** Use `ctx.report_progress()` for percentage updates.
*   [ ] **Client:** Add a listener function for logs in your Session.
*   [ ] **Client:** Add a listener function for progress in your Tool Call.
*   [ ] **Deployment:** Be careful with "Stateless HTTP"—it disables these features!

***