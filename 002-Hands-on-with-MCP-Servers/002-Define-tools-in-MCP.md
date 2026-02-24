# How to Define Tools in MCP

## 1. What is a "Tool" in MCP?
In the MCP universe, a **Tool** is a specific capability you give to the AI (like Claude).
*   **Who controls it?** The AI Model. Claude decides *when* to use it based on the user's conversation.
*   **What does it do?** It performs actions like reading data, calculating numbers, or editing files.
*   **The Big Benefit:** You don't have to write complex JSON schemas manually. The MCP Python SDK does the heavy lifting for you.

## 2. The Recipe: How to Build a Tool
To create a tool, you follow a specific pattern in your Python code: **Decorator → Function → Typing → Logic**.

### Step 1: The Decorator (`@mcp.tool`)
The "magic" happens with a **decorator**. By simply adding `@mcp.tool` above a standard Python function, you tell the MCP server, "This function is a tool that the AI can use".

### Step 2: Define Parameters with Types
The AI needs to know exactly what inputs to provide. You do this using standard Python **type hints**.
*   *Bad:* `def read_file(filename):` (The AI doesn't know what `filename` should look like).
*   *Good:* `def read_file(filename: str) -> str:` (The AI knows to send a text string and expects a text string back).

### Step 3: Add Descriptions (`Field`)
To help the AI understand *context*, you use `Field()` from the `pydantic` library. This allows you to attach a description to every argument so the AI understands the *purpose* of the input.

### Step 4: Write the Logic & Error Handling
Inside the function, you write the actual code.
*   **Logic:** Perform the task (e.g., find a document in a dictionary).
*   **Safety:** Always validate inputs. If a document doesn't exist, raise a `ValueError`. This tells the AI, "I couldn't do that, here is why".

## 3. Real-World Examples
Here are two examples of tools described in the documentation:

### Example A: Reading Data (`read_doc_contents`)
*   **Goal:** Get the text inside a file.
*   **Input:** `doc_id` (String).
*   **Logic:** It looks up the ID in the local dictionary.
*   **Error:** If the ID isn't found, it raises a `ValueError`.

### Example B: Editing Data (`edit_document`)
*   **Goal:** Find and replace text in a document.
*   **Inputs:**
    1.  `doc_id`: The file to edit.
    2.  `old_string`: The text to find.
    3.  `new_string`: The text to replace it with.
*   **Validation:** It checks if the `old_string` actually exists in the file before trying to replace it.

## 4. How to Test Your Tools
Once you have defined your tools, you don't need to build a full chatbot to test them. You can use the **MCP Inspector**.

1.  **Run the Inspector:** Type `mcp dev [your_server_file.py]` in your terminal.
2.  **Visual Interface:** This opens a web page (localhost) where you can see your tools listed on the left.
3.  **Simulate:** You can click a tool, type in arguments (like "report.pdf"), and click "Run Tool."
4.  **Verify:** You will see exactly what the tool returns or if it fails, allowing you to debug before connecting it to Claude.

## 5. Summary Checklist
When defining a tool, make sure you have:
*   [ ] Imported `mcp` and `Field`.
*   [ ] Added the `@mcp.tool` decorator.
*   [ ] Added Type Hints (e.g., `: str`, `: int`) to all arguments.
*   [ ] Added descriptions to arguments using `Field(description="...")`.
*   [ ] Added error handling (`ValueError`) for bad inputs.

## 6. Key Benefits of the SDK Approach

- No manual JSON schema writing required
- Type hints provide automatic validation
- Clear parameter descriptions help Claude understand tool usage
- Error handling integrates naturally with Python exceptions
- Tool registration happens automatically through decorators

The MCP Python SDK transforms tool creation from a complex schema-writing exercise into simple Python function definitions. This approach makes it much easier to build and maintain MCP servers while ensuring Claude receives properly formatted tool specifications.

***