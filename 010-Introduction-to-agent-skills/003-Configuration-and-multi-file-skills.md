# Configuration & Multi-File Skills

## 1. The "Frontmatter": Configuring Your Skill

Every `SKILL.md` file starts with a configuration block (called frontmatter) at the very top. Here is the complete reference of available fields.

### Core Fields

*   **`name`**: The display name for your skill. Optional — defaults to the directory name if omitted.
    *   *Rules:* Use lowercase letters, numbers, and hyphens only. Must be under 64 characters. Must match the directory name for plugin skills.
*   **`description`**: The most important field. This is what Claude reads to decide if it should activate this skill.
    *   *Limit:* Maximum 1,024 characters. Include the exact keywords and phrases you would naturally use when asking for help.

### Invocation Control Fields

*   **`user-invocable`**: Set to `false` to hide the skill from the `/` autocomplete menu. Use for background knowledge that users should not invoke directly. Defaults to `true`.
*   **`disable-model-invocation`**: Set to `true` to prevent Claude from automatically loading this skill via semantic matching. The skill can still be invoked manually via `/skill-name`. Defaults to `false`.
*   **`argument-hint`**: A hint shown during autocomplete to indicate expected arguments. Examples: `[issue-number]`, `[filename] [format]`.

### Capability Fields

*   **`allowed-tools`**: A comma-separated list restricting which tools Claude can use while this skill is active. Listed tools are also pre-approved (no per-use permission prompt).
    *   *Syntax:* `Read, Grep, Glob` or with patterns: `Read, Grep, Bash(python *)`.
    *   *Default:* If omitted, Claude uses its normal, full set of permissions.
*   **`model`**: Specifies a specific AI model version to use for this skill.

### Subagent Fields

*   **`context`**: Set to `fork` to run the skill in a forked subagent context (isolated from main conversation history).
*   **`agent`**: Which subagent type to use when `context: fork` is set. Options: `Explore`, `Plan`, `general-purpose`, or a custom subagent name.

### Advanced Fields

*   **`hooks`**: Hooks scoped to this skill's lifecycle (same syntax as global hooks, but only active when the skill is loaded).

## 2. Writing Perfect Descriptions

If your skill isn't working, it's usually because the description is vague. A good description must answer two specific questions:
1.  **What** does the skill do?
2.  **When** should Claude use it?

**Pro Tip:** Be explicit. Use the actual keywords and phrases you would naturally use when asking for help. If the description matches your phrasing, the skill will trigger reliably.

## 3. Controlling Capabilities (`allowed-tools`)

Sometimes you don't want Claude to have full access to your computer. You can use `allowed-tools` to create "Guardrails."

*   **How it works:** You list exactly which tools are permitted. If a tool isn't on the list, Claude can't use it. Listed tools are also granted without per-use permission prompts.
*   **Syntax examples:**
    *   Simple: `allowed-tools: Read, Grep, Glob`
    *   With patterns: `allowed-tools: Read, Grep, Bash(gh *)`
*   **Use Case:** Creating a "Read-Only" skill for onboarding new developers. You might allow `Read`, `Grep`, and `Glob`, but block any tools that write or delete files.
*   **Default:** If you leave this field blank, Claude uses its normal, full set of permissions.

## 4. Progressive Disclosure: Handling Big Skills

If you try to stuff everything into one 2,000-line `SKILL.md` file, it will use up too much of Claude's "memory" (context window) and be hard to maintain.

The solution is **Progressive Disclosure**:
*   **The Rule:** Keep your main `SKILL.md` file short (under 500 lines).
*   **The Structure:** Move details into subfolders. The standard organization is:
    *   `scripts/` (Executable code)
    *   `references/` (Documentation)
    *   `assets/` (Images or templates)

**How it helps:**
Instead of reading the whole library at once, you link to these files in your `SKILL.md`. Claude will only read the specific reference file *if and when* the user asks a question that requires it. It acts like a "Table of Contents" rather than the whole book.

## 5. Using Scripts Efficiently

You can include executable scripts in your skill folder to handle complex tasks (like data transformation or environment validation).

*   **The Token Hack:** Tell Claude to **run** the script, not **read** it.
*   **Why?** When Claude runs a script, only the *output* counts against your context usage. The code inside the script doesn't take up space in Claude's memory, making it very efficient.

***
