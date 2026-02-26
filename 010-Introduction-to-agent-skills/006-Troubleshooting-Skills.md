# Troubleshooting Claude Code Skills

## 1. The "First Aid" Kit

Before you start guessing what is wrong, use the built-in diagnostic tools to find the problem for you.

*   **The Skills Validator:** This is a command-line tool you can install (often via `uv`). It scans your folders and catches "typos" or structural errors before you even run Claude.
*   **The Debug Flag:** Run `claude --debug` in your terminal. This shows you exactly what is happening "under the hood," including specific error messages if a skill fails to load.

## 2. Scenario A: "It won't start!" (Triggering Issues)

**The Symptom:** Your skill exists, but when you ask Claude to use it, Claude ignores it and does something else.

*   **The Cause:** The **Description** in your `SKILL.md` is likely too vague. Remember, Claude uses "Semantic Matching"—it looks for meaning overlap between your words and the skill description.
*   **The Fix:**
    1.  **Add Keywords:** Include the exact phrases you use in real life (e.g., if you say "Make this faster," add that phrase to the description, not just "Optimization").
    2.  **Be Explicit:** Answer "What does this do?" and "When should I use it?" clearly in the frontmatter.
    3.  **Check `disable-model-invocation`:** If this is set to `true` in the frontmatter, automatic matching is disabled. Use `/skill-name` to invoke it directly instead.

## 3. Scenario B: "It's missing!" (Loading Issues)

**The Symptom:** You ask "What skills are available?" and your skill isn't on the list.

*   **The Cause:** Usually a folder structure mistake.
*   **The Fix:** Check these rules:
    1.  **Named Directory:** Your `SKILL.md` cannot sit loosely in the root `skills` folder. It **must** be inside its own folder (e.g., `~/.claude/skills/my-skill/SKILL.md`).
    2.  **Exact Filename:** The file must be named **`SKILL.md`** exactly. "skill.md" (lowercase) or "README.md" will not work.
    3.  **Hidden from menu?** Check if `user-invocable: false` is set in the frontmatter. This hides the skill from the `/` autocomplete.

## 4. Scenario C: "It's confused!" (Conflicts & Priority)

**The Symptom:** Claude uses the wrong skill, or it ignores your personal version of a skill.

*   **Cause 1: Similarity.** If two skills have descriptions that sound alike, Claude won't know which one to pick.
    *   *Fix:* Make the descriptions distinct.
*   **Cause 2: The Hierarchy.** If you have a personal skill named `code-review`, but your company has an **Enterprise** skill with the same name, the Enterprise one wins.
    *   *The Priority Ladder:* Enterprise (Top) → Personal → Project → Plugins (Bottom).
    *   *Fix:* Rename your personal skill to something unique, like `my-code-review`.

## 5. Scenario D: "It crashed!" (Runtime Errors)

**The Symptom:** The skill starts to run, but then fails with an error message.

*   **Cause 1: Permissions.** If your skill uses a script, it might not have permission to execute.
    *   *Fix:* Run `chmod +x filename.sh` on your scripts.
*   **Cause 2: Paths.** Windows and Mac/Linux use different slashes for file paths (`\` vs `/`).
    *   *Fix:* Always use **forward slashes (`/`)** in your code. They work on all operating systems in this context.
*   **Cause 3: Dependencies.** Your script might be trying to use a tool (like `npm` or `python`) that isn't installed.
    *   *Fix:* List these requirements clearly in your skill description.

## 6. Summary Checklist

If you are stuck, run through this quick list:

*   [ ] **Not Triggering?** Rewrite the description with more natural keywords. Check `disable-model-invocation` is not `true`.
*   [ ] **Not Loading?** Check that the file is named `SKILL.md` and sits in its own folder. Check `user-invocable` is not `false`.
*   [ ] **Wrong Skill?** Check for naming conflicts or unclear descriptions.
*   [ ] **Shadowed?** Check if an Enterprise skill is overriding yours (rename yours if needed).
*   [ ] **Plugin Missing?** Clear the cache and reinstall. Use fully-qualified name `/plugin-name:skill-name`.
*   [ ] **Runtime Fail?** Check file permissions (`chmod +x`) and use forward slashes (`/`).

***