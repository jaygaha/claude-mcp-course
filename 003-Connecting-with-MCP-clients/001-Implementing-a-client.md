# Implementing an MCP Client

## 1. What is the Client's Job?
Before writing code, it is important to understand that the **MCP Client** acts as a "wrapper" or interface.
*   **It does NOT run the tools:** The Server does that.
*   **It DOES manage the conversation:** It connects your application (like a chatbot) to the Server.
*   **The Analogy:** If the Server is a library full of books (data/tools), the Client is the librarian who goes to fetch what you ask for,.

## 2. Key Concepts for Setup
To build a client, you need to handle three specific technical things:

### A. The "Session" (The Connection)
Your code interacts with a **`ClientSession`**. This is the active phone line between your app and the server.
*   **Cleanup is Vital:** You cannot just open a connection and leave it. You must use "Async Enter/Exit" functions to ensure the connection closes properly when the app shuts down (Resource Cleanup),.

### B. Transport (The Wire)
You need to decide how to talk to the server.
*   **Standard Input/Output (stdio):** The most common method for beginners where the Client and Server run on the same computer.

### C. Dependencies
You will generally use the **MCP Python SDK**, along with standard libraries like `json` and `pydantic` (specifically `AnyUrl` for handling addresses).

## 3. Step-by-Step Implementation

### Step 1: The Connection Wrapper
It is best practice to wrap your client logic in a Python class rather than writing loose scripts. This keeps your code organized.

### Step 2: Implementing Tools (The "Hands")
Tools allow the AI to *do* things.
1.  **List Tools:** create a function `list_tools()` that calls `await self.session.list_tools()`. This asks the server, "What can you do?".
2.  **Call Tool:** create a function `call_tool()` that sends the tool name and arguments to the server. The server executes it and sends back the result.

### Step 3: Implementing Resources (The "Eyes")
Resources allow the App to *read* data (like files).
1.  **Read Resource:** Create a function that takes a URI (address).
    *   Code: `await self.session.read_resource(AnyUrl(uri))`.
2.  **Parse Data:** The server sends back data with a "MIME type" (label).
    *   If it is `application/json`, use `json.loads()`.
    *   Otherwise, read it as plain text.

### Step 4: Implementing Prompts (The "Scripts")
Prompts are pre-written templates.
1.  **List Prompts:** `await self.session.list_prompts()` to see what templates exist.
2.  **Get Prompt:** `await self.session.get_prompt(name, args)`. This fills in the blanks of the template (e.g., inserting a specific document ID) and returns a message ready for the AI.

## 4. The Data Flow (How it works in practice)
When you run your client, the conversation flows like this:

1.  **Request:** Your App asks, "What tools do we have?"
2.  **Listing:** The Client calls `list_tools()` and gives the list to Claude.
3.  **Selection:** Claude says, "I want to use the `read_file` tool."
4.  **Execution:** The Client calls `call_tool()`.
5.  **Response:** The Server reads the file and returns the text to the Client.
6.  **Final Answer:** The Client gives the text to Claude to read.

## 5. Testing Your Client
*   **Test Harness:** You can run your `client.py` file directly with a simple test script to ensure it can connect and list tools before hooking it up to a complex AI.
*   **Integration:** Once the client works, you connect it to the LLM (Large Language Model) so users can ask natural questions like "What is in report.pdf?".

***