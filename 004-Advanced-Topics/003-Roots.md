# Beginner Notes: MCP Roots

## 1. What is a "Root"?
Think of a **Root** as a "Safe Zone" or a "Sandbox" on your computer.

*   **Definition:** A Root is a specific file or folder that the user explicitly grants the MCP Server permission to access.
*   **The Rule:** If a folder is not a "Root," the Server (and therefore Claude) cannot touch it. This acts as a security boundary.

## 2. The Problem: Why do we need them?
Without Roots, working with files is annoying and limited:
1.  **The "Blindness" Problem:** Claude doesn't know what files are on your computer. It can't "look around" your hard drive to find things.
2.  **The "Long Path" Problem:** To use a tool (like "Convert Video"), the user would have to type the exact, full path (e.g., `/Users/JayGaha/Documents/Projects/Videos/bikin.mp4`). If you make a typo, it fails.

## 3. The Solution: "Autonomous Discovery"
By defining Roots, you give Claude the ability to search for files itself. To make this work, an MCP Server typically provides three tools:

1.  **`ListRoots`**: A tool that asks, "Which folders am I allowed to look in?"
2.  **`ReadDirectory`**: A tool that asks, "What files are inside this specific folder?"
3.  **The Action Tool**: The actual tool you wanted to use (e.g., `ConvertVideo`).

**The Result:** You can just say, *"Convert the video named 'bikin.mp4'."* Claude will look through the **Roots**, find the file, and convert it without needing the full path.

## 4. Key Benefits
Using Roots offers two main advantages:
*   **Permission Control:** It limits the server's access. The server can *only* see what is inside the authorized roots, keeping the rest of your computer private.
*   **Autonomous Discovery:** It allows the AI to be smart. Claude can search through the allowed folders to find the right file without you holding its hand.

## 5. Important Warning for Developers
If you are building an MCP server, there is a critical safety catch:

*   **No Auto-Security:** The MCP SDK does **not** automatically stop the server from accessing files outside the root.
*   **Manual Check Required:** You (the developer) must write code to enforce this. You need to implement a function like `is_path_allowed()` to check if the file the user asked for is actually inside one of the granted Roots.

***