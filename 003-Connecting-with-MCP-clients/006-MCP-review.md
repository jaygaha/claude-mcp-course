# MCP Review: The "Cheat Sheet"

## 1. The Big Picture: Architecture Review
To recap, MCP is the **communication layer** that saves you from writing boring code. It splits the world into two parts:

*   **The Client (The "Face"):** This is your App or Chatbot. It talks to the user and asks for things.
*   **The Server (The "Brain"):** This is where the work happens. It holds the **Primitives** (Tools, Resources, Prompts).

## 2. The Three Primitives (The Core Review)
The most important part of learning MCP is understanding the three "Primitives" (capabilities) a server can provide. The best way to remember them is by asking: **"Who is in control?"**

### A. Tools (Model-Controlled)
*   **Who drives?** The AI (Claude).
*   **The Vibe:** "I need to *do* something."
*   **Usage:** Used to add new capabilities to the AI, like running calculations, executing code, or calling APIs.
*   **Example:** A calculator tool or a "GitHub Issue Creator."

### B. Resources (App-Controlled)
*   **Who drives?** The Application Code.
*   **The Vibe:** "I need to *read* something."
*   **Usage:** Used to fetch data to display in your UI (like a list of files) or to secretly feed context to the AI before it answers.
*   **Example:** A list of documents in Google Drive.

### C. Prompts (User-Controlled)
*   **Who drives?** The User.
*   **The Vibe:** "I need to *start* something."
*   **Usage:** Used for pre-defined workflows. These are usually buttons or "Slash Commands" that trigger a specific, high-quality template.
*   **Example:** A "Chat Starter" button or a `/fix-bug` command.

## 3. Decision Matrix: When to use what?
If you are building an MCP Server and don't know which one to pick, use this simple logic flow:

1.  **Do you need Claude to have a new ability?** (e.g., math, API access)
    *   **Build a Tool.**
2.  **Do you need your App to show data to the user?** (e.g., a file list)
    *   **Build a Resource.**
3.  **Do you want to give the user a shortcut?** (e.g., a button to "Summarize")
    *   **Build a Prompt.**

## 4. The Development Lifecycle Review
Here is the standard recipe for building with MCP:

1.  **Define:** Write your functions in Python using decorators (`@mcp.tool`, `@mcp.resource`).
2.  **Inspect:** Run `mcp dev` to test your tools in the browser **MCP Inspector**. (Don't skip this!).
3.  **Connect:** Build a simple **Client** that connects to your server.
4.  **Integrate:** Hook the Client up to Claude so he can actually use the tools you built.

***