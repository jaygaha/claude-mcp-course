# What are Claude Code Skills?

## 1. The Core Concept

**Skills** are reusable instructions that teach Claude Code how to handle specific tasks automatically.

*   **The Problem:** You often find yourself repeating the same instructions to Claude (e.g., "Review this code using these specific rules" or "Write the commit message in this specific format").
*   **The Solution:** Instead of typing these instructions every time, you write them once in a **Skill**. Claude then applies that knowledge automatically whenever the task comes up.
*   **Format:** A skill is simply a **Markdown file** named `SKILL.md` inside its own directory.

## 2. How It Works

Skills work through two complementary mechanisms: **automatic discovery** and **direct invocation**.

### Automatic Discovery (Semantic Matching)

1.  **Frontmatter:** Every skill file starts with a header called "frontmatter" containing a `name` and a `description`.
    ```yaml
    ---
    name: pr-review
    description: Reviews pull requests for code quality...
    ---
    ```
2.  **Matching:** When you ask Claude to do something (like "Review this PR"), Claude compares your words against the **descriptions** of all available skills.
3.  **Activation:** If your request matches a skill's description, Claude automatically loads that skill and follows its instructions.

### Direct Invocation (Slash Commands)

You can also invoke any skill directly by typing `/skill-name` in the prompt. This bypasses semantic matching entirely and loads the skill immediately, making it useful when you know exactly which skill you want.

## 3. Where Do Skills Live?

You can store skills in several places, depending on who needs to use them:

### A. Personal Skills

*   **Location:** `~/.claude/skills/<skill-name>/SKILL.md`
*   **Behavior:** These follow **you** across all your projects. Use this for your personal preferences, like how you like code explained or your specific documentation style.

### B. Project Skills (For the Team)

*   **Location:** `.claude/skills/<skill-name>/SKILL.md` inside the root folder of a specific repository.
*   **Behavior:** These are shared with anyone who clones the code. This is perfect for **team standards**, like company brand guidelines, strict coding rules, or web design colors.
*   **Monorepo support:** Claude Code automatically discovers skills from nested `.claude/skills/` directories (e.g., `packages/frontend/.claude/skills/`), making it well suited for monorepo setups.

### C. Plugin Skills

*   **Location:** `<plugin>/skills/<skill-name>/SKILL.md`
*   **Behavior:** Distributed via plugins and namespaced as `/plugin-name:skill-name` to avoid conflicts.

### D. Enterprise Skills

*   **Location:** Configured via managed settings by administrators.
*   **Behavior:** Mandatory rules that override all other skills with the same name.

## 4. Hot-Reload: No Restart Needed

Skills created or modified in `~/.claude/skills/` or `.claude/skills/` are **immediately available** without restarting the session. Claude Code detects changes automatically.

Plugin-provided skills are also available immediately after installation.

## 5. Skills vs. Other Options

Claude Code has several ways to customize behavior. Here is how to tell them apart:

| Feature | How it works | Best used for... |
| :--- | :--- | :--- |
| **CLAUDE.md** | **Always On.** Loads into *every* conversation automatically. | Global rules you *always* want (e.g., "Always use TypeScript strict mode"). |
| **Slash Commands** | **Manual.** You must type them explicitly (e.g., `/help`). | Actions you want to trigger yourself intentionally. |
| **Skills** | **On-Demand.** Loads automatically when relevant, or via `/skill-name`. | Specific tasks that don't need to fill up the memory all the time (e.g., a checklist for debugging). |

## 6. When Should You Write a Skill?

The "Rule of Thumb" is simple: **If you find yourself explaining the same thing to Claude repeatedly, that is a skill waiting to be written.**

Common examples include:
*   **Code Reviews:** Teaching Claude your team's specific checklist for approving code.
*   **Commit Messages:** Enforcing a specific format for saving changes.
*   **Brand Guidelines:** Ensuring Claude uses the correct colors and fonts for design tasks.
*   **Documentation:** Generating docs that match a specific template.
