# How to Setup and Use the MCP Inspector

## 1. What is the MCP Inspector?
The **MCP Inspector** is a special developer tool that lets you test your MCP Server directly in your web browser.

*   **The Problem:** Normally, to test your server, you have to build a full Client application (like a chatbot) to talk to it. This is slow and annoying if you just want to check if a function works.
*   **The Solution:** The Inspector acts as a "fake client." It gives you a visual interface to click buttons and run your tools manually to make sure they work before you connect them to a real AI.

## 2. How to Launch It
You don't need to install a separate app; it runs from your command line (terminal).

1.  **Open your Terminal:** Go to the folder where your project is.
2.  **Activate Environment:** Make sure your Python environment is active (if you are using one).
3.  **Run the Command:** Type the following command:
    ```bash
    mcp dev [your_server_file.py]
    ```
    *(Replace `[your_server_file.py]` with the actual name of your python script)*.

Once you run this, the Inspector will start your server and provide a **localhost address** (a web link) for you to click.

## 3. The Interface
When you open the link in your browser, you will see a dashboard divided into sections:

*   **Left Sidebar:** This is your connection center. It shows the status of your server and has a "Connect" button.
*   **Top Navigation:** You will see tabs for the three main MCP features: **Resources**, **Prompts**, and **Tools**.
*   **Main Area:** This updates based on what you select. For example, in the "Tools" section, you will see a list of every tool you defined in your code.

## 4. How to Test a Tool (Step-by-Step)
This is the most common use case. You want to see if your code actually runs when the AI asks for it.

1.  **Select a Tool:** Click on a tool name in the list (e.g., `read_doc_contents`).
2.  **Input Parameters:** A panel will open on the right. If your tool requires inputs (like a `doc_id`), you will see text boxes where you can type them in manually.
3.  **Run:** Click the **Run Tool** button.
4.  **Verify:** The Inspector will show you the "Success" or "Failure" message and the actual data returned. This lets you see exactly what the AI would see.

## 5. Why is this useful?
*   **Live Debugging:** You can change your code, restart, and test immediately.
*   **Simulation:** It simulates exactly how an AI (like Claude) calls your tools, so you can catch errors (like missing files or wrong variable types) early.
*   **No "Middleman":** You don't have to worry about the Client code crashing; you are testing the Server logic in isolation.

***