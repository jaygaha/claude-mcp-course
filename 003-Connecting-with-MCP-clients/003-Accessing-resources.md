# How to Setup "Accessing Resources"

## 1. What does "Accessing a Resource" mean?
In the MCP world, **Resources** are like files or data feeds that live on the Server.
*   **The Goal:** Your Client Application needs to "read" this data to show it to the user or feed it to the AI.
*   **Who is in Control?** The **Application** controls this. Unlike Tools (which the AI asks for), Resources are fetched whenever your code decides it needs them.

## 2. Prerequisites (What you need)
Before writing the code, ensure your Python file imports these two specific libraries:
*   `json`: To read data structures (like lists or dictionaries).
*   `pydantic.AnyUrl`: To properly format the address (URI) of the resource.

## 3. Step-by-Step Implementation
To access a resource, your Client must send a specific request to the Server. Here is the recipe:

### Step 1: define the `read_resource` function
You need a function in your client that takes a **URI** (the address of the resource, like `file:///report.txt`) as an input.

### Step 2: Call the Session
Inside that function, use the SDK command to ask the server for the data.
*   **Code:** `await self.session.read_resource(AnyUrl(uri))`
*   **Note:** You must wrap the string URI in `AnyUrl()` so the system accepts it.

### Step 3: Extract the Content
The Server returns a result object. The actual data is usually inside a list called `contents`.
*   **Code:** `content = result.contents` (This gets the first item found).

### Step 4: Check the "MIME Type" (Crucial Step!)
The Server sends the data back as a string, but it also sends a "MIME type" label (like a sticker on a box) to tell you what format it is. You need to write logic to handle this:

*   **Scenario A: It is JSON (`application/json`)**
    *   This means the data is a list or dictionary.
    *   **Action:** Use `json.loads(content.text)` to convert the text string back into a real Python object.
*   **Scenario B: It is Text (`text/plain`)**
    *   This means it is just a standard text file.
    *   **Action:** Just use `content.text` directly.

## 4. Code Snapshot
Here is what the logic looks like in simple Python/Pseudo-code:

```python
async def read_resource(self, uri: str):
    # 1. Ask the server for the resource
    result = await self.session.read_resource(AnyUrl(uri))

    # 2. Get the specific item
    resource = result.contents

    # 3. Decide how to read it based on the label (MIME Type)
    if resource.mime_type == "application/json":
        # It's a data structure, decode it
        return json.loads(resource.text)
    else:
        # It's just text, return it as is
        return resource.text
```

## 5. Real-World Use Case
Why would you do this?
*   **Context for the AI:** You might write a script where the user selects a document from a list. Your app "Accesses the Resource" to get the text, and then pastes that text secretly into the prompt so the AI knows what you are talking about.
*   **UI Display:** You might fetch a list of files to display them in a CLI (Command Line Interface) menu for the user to choose from.

***