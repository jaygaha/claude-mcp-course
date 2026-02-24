# How to Define Resources in MCP

## 1. What is a "Resource"?
In MCP, a **Resource** is a way for the Server to share **data** with the Client application.

*   **Who controls it?** The **Application** (Code). Unlike "Tools" (which the AI decides to use), "Resources" are fetched whenever the application code needs them.
*   **What is it used for?** It gives the app context. For example, getting a list of files to show in a dropdown menu, or reading the text of a specific document to show to the user,.
*   **Analogy:** If Tools are the "Hands" (doing work), Resources are the "Eyes" (reading information).

## 2. The Two Types of Resources
When defining resources, you typically create two kinds:

### A. Static Resources (Direct)
*   **What:** A fixed address to get specific data.
*   **Example:** `docs://list` might return a list of all available documents.
*   **URI:** Uses a static path.

### B. Templated Resources (Dynamic)
*   **What:** An address with "wildcards" (variables) to get specific items.
*   **Example:** `docs://{id}` allows the app to ask for "document 1" or "document 5" using the same function.
*   **URI:** Uses parameters like `{doc_id}`.

## 3. How to Define a Resource (Server-Side)
To create a resource, you use a specific "recipe" in your Python code: **Decorator → URI → Function**.

### Step 1: The Decorator (`@mcp.resource`)
Just like tools, you use a decorator. You must provide a **URI** (Uniform Resource Identifier), which acts like a URL or web address for your data.

```python
@mcp.resource("docs://{doc_id}") 
```

### Step 2: The Function & Parameters
Write a Python function to fetch the data.
*   **Input:** If your URI has a wildcard (like `{doc_id}`), that becomes an argument in your function.
*   **Logic:** The code retrieves the data (e.g., looking up a file in a dictionary).

### Step 3: Return Data & MIME Type
You cannot just return raw data; you must give the client a hint about what kind of data it is. This is called the **MIME Type**.
*   **`text/plain`**: For simple text files.
*   **`application/json`**: For structured data (like lists or dictionaries).

**Example Logic:**
> If I return a list of files, I label it `application/json` so the Client knows to parse it as a list.

## 4. How the Client Uses It (The Flow)
Once you define the resource on the Server, here is how the Client "consumes" it:

1.  **Request:** The Client code calls `read_resource(uri)` using the specific address you defined.
2.  **Matching:** The Server matches the URI to your function.
3.  **Execution:** Your function runs and returns the data.
4.  **Parsing:** The Client checks the `mime_type`. If it is JSON, it converts it into a Python object/dictionary. If it is text, it reads it as a string.

## 5. Summary Checklist
When defining a resource, ensure you have:
*   [ ] Used the `@mcp.resource("...")` decorator.
*   [ ] Defined a clear URI pattern (e.g., `myserver://data`).
*   [ ] Matched function arguments to any URI wildcards (e.g., `{id}`).
*   [ ] Returned the data as a string (the SDK handles serialization).
*   [ ] Defined the correct MIME type so the client knows how to read it.

***