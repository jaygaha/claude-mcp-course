# Skills vs. Other Features: Choosing the Right Tool

## 1. The Big Picture

Claude Code offers many ways to customize how the AI works. It can be confusing to know which one to use.
*   **The Rule of Thumb:** Don't try to force everything into a Skill. Each feature has a specific superpower.
*   **The Goal:** Use the right tool for the right job to keep Claude fast and smart.

## 2. Skills vs. `CLAUDE.md` (The "Always On" vs. "On Demand")

Think of `CLAUDE.md` as the rules posted on the office wall, while Skills are the instruction manuals in the filing cabinet.

### `CLAUDE.md`

*   **Behavior:** **Always On.** It loads into *every* single conversation you start.
*   **Best For:** Global project rules that must never be broken.
    *   "Always use TypeScript strict mode."
    *   "Never modify the database schema directly."
    *   "Follow this specific coding style."

### Skills

*   **Behavior:** **On Demand.** It only loads when you actually need it.
*   **Best For:** Specific tasks that you only do sometimes.
    *   A checklist for reviewing a Pull Request (PR).
    *   A template for writing documentation.
    *   *Why?* You don't need the PR checklist clogging up Claude's memory when you are just debugging a simple error.

## 3. Skills vs. Slash Commands (Automatic vs. Manual)

This comes down to how much work *you* want to do.

### Slash Commands (e.g., `/help`)

*   **Trigger:** **Manual.** You must explicitly type the command to make it happen.
*   **Best For:** Actions you want to trigger intentionally and precisely.

### Skills

*   **Trigger:** **Automatic.** Claude reads your natural language request (e.g., "Check this code") and finds the matching skill for you.
*   **Best For:** When you want a magical experience where Claude "just knows" what to do based on the context.

## 4. Skills vs. Subagents (Context vs. Isolation)

Both help with tasks, but they live in different places.

### Subagents

*   **Behavior:** **Isolation.** They run in a separate "room." They receive a task, work on it independently, and come back with the result.
*   **Best For:** Delegating work.
    *   "Go fix this bug while I talk about something else."
    *   Tasks that need different tool permissions than your main chat.

### Skills

*   **Behavior:** **Enhancement.** They join your *current* conversation.
*   **Best For:** Teaching Claude how to handle the *current* topic better.
    *   "Here is the knowledge you need to answer my question right now."

## 5. Skills vs. Hooks (Requests vs. Events)

This is about *what* triggers the action.

### Hooks

*   **Trigger:** **Events.** They fire automatically when something technical happens, like saving a file or running a specific tool.
*   **Best For:** Automated chores.
    *   "Run the linter every time I save a file."
    *   "Validate input before running a tool."

### Skills

*   **Trigger:** **Requests.** They fire based on what you *ask* Claude to do.
*   **Best For:** Guidelines and reasoning.
    *   "When I ask for a review, use this specific reasoning process."

## 6. Skills vs. MCP Servers (Knowledge vs. Tools)

This is the difference between "Knowing" and "Doing."

### MCP Servers

*   **Role:** **The Tools.** They provide the capabilities and connections to the outside world.
*   **Examples:** Connecting to a database, searching Google, or accessing your Calendar.

### Skills

*   **Role:** **The Instructions.** They teach Claude *how* to use those tools properly.
*   **Example:** An MCP Server lets Claude access GitHub; a Skill teaches Claude your team's specific rules for writing a GitHub Issue.

## Summary Cheat Sheet

| Feature | Best Used For... | Trigger |
| :--- | :--- | :--- |
| **CLAUDE.md** | Rules you want active **100% of the time** (Global Standards). | Always active |
| **Skills** | Specialized knowledge for **specific tasks** (PRs, Docs). | Automatic (Natural Language) |
| **Slash Commands** | Actions you want to control **manually**. | Typing `/` |
| **Subagents** | **Delegating** work to run in the background. | Explicit request |
| **Hooks** | **Automating** cleanup or validation steps. | Events (Save/Run) |
| **MCP Servers** | Giving Claude **new capabilities** (Tools/Data). | Connection |

***