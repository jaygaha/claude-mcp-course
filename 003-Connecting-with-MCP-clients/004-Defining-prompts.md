# How to Define Prompts in MCP

## 1. What is a "Prompt" in MCP?
In the MCP world, a **Prompt** is a reusable, pre-written template for a conversation.
*   **Who controls it?** The **User**. Unlike Tools (which the AI chooses to use) or Resources (which the App fetches automatically), Prompts are usually triggered by a user clicking a button or typing a command (like `/fix-bug`).
*   **The Goal:** instead of forcing users to type long, complex instructions every time, the Server provides "Certified High-Quality Prompts" that are guaranteed to work well.
*   **Analogy:** Think of it like a "Mad Libs" game. The Server provides the story template, the User provides the specific words (arguments), and the AI reads the finished story.

## 2. Why use them?
*   **Quality Control:** Developers can write optimized prompts that generate the best results, rather than hoping the user asks the question correctly.
*   **Efficiency:** It saves time. A user can just type `/summarize` instead of "Please read this file and summarize it for me...".
*   **Context Injection:** The server can automatically insert complex data (like code snippets or logs) into the prompt behind the scenes.

## 3. How to Define a Prompt (Server-Side)
To create a prompt, you follow a pattern very similar to Tools and Resources: **Decorator → Function → Return Messages**.

### Step 1: The Decorator
You use the `@mcp.prompt()` decorator. You should give it a name (which the user sees) and a description.
*   *Example:* `@mcp.prompt(name="review_code", description="Reviews code for errors")`.

### Step 2: The Function & Arguments
Define a Python function. The arguments you define here become the "blanks" the user needs to fill in.
*   *Input:* `def review_code(code_id: str):`
*   *Logic:* The function takes this input (like a file ID) and prepares a message.

### Step 3: The Return Value (The Message)
This is the most important part. The function does **not** run the AI. It returns a **list of messages** that *will be sent* to the AI.
*   **Format:** You return a list containing objects with a `role` (usually "user") and `content` (the text instructions).
*   **Template Logic:** You insert the arguments into the text string (e.g., `f"Please review the document {doc_id}..."`).

## 4. Real-World Example: The "Format" Command
Source describes a prompt designed to rewrite a document in Markdown.

**The Code Pattern:**
```python
@mcp.prompt(name="format", description="Rewrites a document in markdown")
def format_document(doc_id: str) -> list[Message]:
    # 1. Create the instruction text
    instruction = f"Please read the document located at {doc_id} and rewrite it."

    # 2. Return it as a user message
    return [
        UserMessage(content=instruction)
    ]
```

## 5. How the Client Uses It
Once you have defined the prompt on the server, the Client (the App) accesses it in two steps:

1.  **List Prompts:** The Client asks `await self.session.list_prompts()` to show the user a menu of available commands (e.g., a "Format Document" button).
2.  **Get Prompt:** When the user clicks the button, the Client calls `await self.session.get_prompt("format", arguments)`.
    *   The Server runs the logic, fills in the template, and sends the finished text back.
    *   The Client takes that text and sends it to Claude to start the conversation,.

## 6. Summary Checklist
*   [ ] Use the `@mcp.prompt` decorator.
*   [ ] Give the prompt a clear `name` and `description`.
*   [ ] Define arguments (like `doc_id`) so the server knows what data to insert.
*   [ ] Return a list of `UserMessage` objects.
*   [ ] **Remember:** Prompts *serve the User*. Use them for workflows where the user initiates the action (like "Slash Commands").

***