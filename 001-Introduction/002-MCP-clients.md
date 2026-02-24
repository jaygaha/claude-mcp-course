# MCP clients

1. What is an MCP Client?

    An **MCP Client** is the software or application that "hosts" the conversation with the AI. It acts as the bridge (interface) between the AI model (like Claude) and the **MCP Server** (where the actual tools and data live).

    Think of the Client as a **Manager**:

    - It doesn't do the manual labor itself (that's the Server's job).
    - It doesn't generate the intelligence (that's the AI's job).
    - It coordinates the communication between the two.

2. The "Middleman" Role

    The most important thing to understand is that the Client acts as an intermediary. It facilitates the message exchange but does not execute the tools itself.

    - The AI says: "I need to check the weather."
    - The Client says to the Server: "Hey, run the get_weather tool."
    - The Server runs the code and gives the result to the Client.
    - The Client passes that result back to the AI.

3. How It Connects (Transport)

    MCP Clients are "**Transport Agnostic**." This is a fancy way of saying they can connect to servers in different ways, just like you can talk to a friend via text, email, or phone.

    Common connection methods include:
    
    - **Stdin/Stdout**: Running the client and server on the same computer (most common for beginners).
    - **HTTP/WebSockets**: Connecting over the internet.

4. Key Responsibilities (What does it actually do?)

    To make the magic happen, the Client handles three specific types of requests:

    A. **Managing Tools**

    Tools are capabilities (like a calculator or database search).

    - `list_tools()`: The Client asks the Server, "What tools do you have available?",.
    - `call_tool()`: When the AI decides to use a tool, the Client sends a request to the Server to actually run it with specific arguments,.

    B. Accessing Resources

    Resources are data sources (like files or logs).
    
    - `read_resource()`: The Client requests specific data using a URI (a link address like file:///report.pdf). The Server sends the data back, often as text or JSON,.

    C. Using Prompts

    Prompts are pre-written templates for specific workflows.
    - `list_prompts()` & `get_prompt()`: The Client can ask the Server for a template (e.g., "Summarize this bug report"). The Server fills in the details and sends back a perfect message for the AI to process,.

5. The Workflow Loop

    Here is the step-by-step lifecycle of an MCP interaction:

    1. **Start**: The Application/User wants to ask Claude a question.
    2. **Discovery**: The Client asks the Server: "List your tools."
    3. **Context**: The Client sends the User's query plus the list of available tools to Claude.
    4. **Decision**: Claude looks at the query and says, "I need to use Tool X."
    5. **Execution**: The Client tells the Server: "Call Tool X with these inputs."
    6. **Result**: The Server runs the tool and hands the result back to the Client.
    7. **Final Answer**: The Client gives the result to Claude, and Claude writes the final answer for the user.

6. Technical "Need-to-Knows" for Coding

    If you are looking at the code for an MCP Client, you will see a few common patterns:
    
    - **Sessions**: The connection is often wrapped in a "Client Session." This manages the active connection to the server.
    - **Cleanup**: Because the Client opens a connection, it must also close it properly (resource cleanup) when the application shuts down.
    - **Async/Await**: Clients usually communicate asynchronously. You will see Python commands like await self.session.call_tool(...) so the app doesn't freeze while waiting for the Server to reply.