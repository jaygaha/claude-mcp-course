# How to Setup "Prompts" in the MCP Client

## 1. The Concept: What are we building?
When you implement Prompts in a Client, you are giving your application a way to use **"Pre-filled Templates."**

*   **Who starts it?** The **User**. Prompts are typically triggered by a user clicking a button (like "Chat Starter" buttons) or typing a specific command (like `/fix-code`).
*   **What happens?** Instead of the user typing a long, complicated request manually, the Client asks the Server for a professionally written prompt, fills in the blanks (like a specific filename), and sends it to the AI.

## 2. The Two Main Functions
To make this work, your Client needs to perform two specific actions:

### Action A: Discovery ("What templates do you have?")
Your application needs to know what prompts are available so it can show them to the user (e.g., in a dropdown menu or a list of slash commands).
*   **The Command:** `list_prompts()`
*   **The Code:** `await self.session.list_prompts()`
*   **Result:** The server returns a list of names and descriptions (e.g., `name="format"`, `description="Rewrites a document in markdown"`).

### Action B: Retrieval ("Fill out this template.")
When the user selects a prompt, you need to get the actual text to send to the AI.
*   **The Command:** `get_prompt()`
*   **The Code:** `await self.session.get_prompt(prompt_name, arguments)`
*   **The Arguments:** You pass a dictionary of inputs (like `{"doc_id": "report.pdf"}`) that the server uses to fill in the "blanks" of the template.

## 3. The Workflow Loop
Here is the step-by-step flow of how a Client handles a prompt:

1.  **User Action:** The user types a command, for example, `/format report.pdf`.
2.  **Client Request:** The Client calls `get_prompt("format", {"doc_id": "report.pdf"})`.
3.  **Server Magic:** The Server takes the template ("Please rewrite {doc_id}...") and fills it in ("Please rewrite report.pdf...").
4.  **The Return:** The Server sends back a **List of Messages** (not just a string).
5.  **Handoff:** The Client takes these messages and feeds them into the AI (Claude) as the start of the conversation.

## 4. Why is this useful for Beginners?
*   **No "Prompt Engineering" needed:** You don't have to teach your users how to write perfect prompts. The Server developer has already done that.
*   **Dynamic Content:** You can insert complex data (like file contents or error logs) into the prompt automatically without the user having to copy-paste anything.

## 5. Summary Checklist
When writing your Client code for prompts, ensure you:
*   [ ] Create a function to **List** available prompts so the user knows what they can do.
*   [ ] Create a function to **Get** a specific prompt using its name.
*   [ ] Allow passing **Arguments** (dictionaries) so the prompt can be customized.
*   [ ] Remember that the result is a **Message Object** (ready to be sent to the AI), not just a plain string.

***