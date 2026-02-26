# Creating Your First Skill in Claude Code

## 1. The Goal

We are going to build a **Personal Skill**.
*   **The Task:** Teaching Claude how to write a Pull Request (PR) description in a specific format automatically.
*   **The Benefit:** Instead of typing "Please check the diff and write a PR description with these headings...", you just say "Write a PR," and Claude knows exactly what to do.

## 2. Step-by-Step Implementation

### Step A: Create the Folder

Skills live in directories. For a personal skill (available in all your projects), you create a folder inside your home directory.
*   **Command:**
    ```bash
    mkdir -p ~/.claude/skills/pr-description
    ```
*   **Rule:** The directory name (`pr-description`) should match your skill name.

### Step B: Create the File (`SKILL.md`)

Inside that folder, you must create a file named exactly **`SKILL.md`**. This file has two distinct parts separated by dashes (`---`).

#### Part 1: The Frontmatter (The ID Card)

The top of the file tells Claude *what* this skill is and *when* to use it.

```yaml
---
name: pr-description
description: Writes pull request descriptions. Use when creating a PR, writing a PR, or when the user asks to summarize changes for a pull request.
---
```

*   **Name:** The display name for the skill. This is optional — if omitted, Claude uses the directory name. Use lowercase letters, numbers, and hyphens only (max 64 characters).
*   **Description:** **Crucial!** This is what Claude reads to decide if your request matches this skill (max 1,024 characters).

#### Part 2: The Instructions (The Brains)

Below the second set of dashes, you write the actual instructions in Markdown.

```markdown
When writing a PR description:
1. Run `git diff main...HEAD` to see all changes on this branch
2. Write a description following this format:

## What
One sentence explaining what this PR does.

## Why
Brief context on why this change is needed.

## Changes
- Bullet points of specific changes made
```

## 3. How to Test It

1.  **No restart needed:** Skills hot-reload automatically. As soon as you save `SKILL.md`, it becomes available in your current session.
2.  **Verify:** Check the available skills list to see if `pr-description` appears, or type `/pr-description` to invoke it directly.
3.  **Run:** Make some code changes, then ask Claude: *"Write a PR description for my changes."*
    *   Claude will recognize the intent, confirm it is using the skill, and generate the text using your template.


## 4. How Skill Matching Works

It is important to understand what happens "under the hood" when you type a prompt:

1.  **Scanning:** When Claude starts, it scans your skill folders but **only reads the names and descriptions** (not the full instructions yet).
2.  **Semantic Matching:** When you type a request (e.g., "Summarize my edits"), Claude compares your words against the **Descriptions** of all available skills.
3.  **Confirmation:** Once it finds a match, Claude asks you to **confirm** before loading the full instructions into its context.

## 5. The Priority Hierarchy

What happens if you have two skills with the same name? Claude follows a strict order of operations to decide which one "wins":

1.  🥇 **Enterprise:** Managed settings (Highest Priority).
2.  🥈 **Personal:** Your home directory (`~/.claude/skills`).
3.  🥉 **Project:** The `.claude/skills` folder inside the specific repository you are working in.
4.  🏅 **Plugins:** Installed plugins (Lowest Priority).

*Tip: To avoid conflicts, give your skills specific names like `frontend-review` instead of just `review`.*

## 6. Managing Skills

*   **To Update:** Edit the text inside `SKILL.md`. Changes are picked up automatically via hot-reload.
*   **To Remove:** Delete the directory entirely.
*   **To Invoke Directly:** Type `/skill-name` in the prompt to bypass semantic matching.

***