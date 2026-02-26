# How to Share Skills in Claude Code

## 1. Why Share?

A skill is useful if it helps *you*, but it is powerful if it helps *everyone*.
*   **The Goal:** Sharing skills standardizes how your team works. It ensures everyone reviews code the same way, writes documentation in the same format, and follows the same security rules.

## 2. The Three Ways to Share

There are three main methods to distribute skills, depending on who needs them.

### Method A: Repository Commits (The "Team" Way)

This is the simplest method for teams working on the same project.

*   **How:** Place your skill folders inside the `.claude/skills` directory of your project.
*   **Distribution:** Commit these files to Git.
*   **Result:** Anyone who **clones the repository** automatically gets these skills. No extra installation is needed.
*   **Best For:** Project-specific workflows and team coding standards.

### Method B: Plugins (The "Community" Way)

This is for skills that are useful across many different projects, not just one.
*   **How:** Package your skills into a Plugin project (using the same folder structure) and distribute it via a marketplace.
*   **Distribution:** Other users "install" the plugin.
*   **Best For:** General tools or utilities you want to share with the wider world or across different teams.

### Method C: Enterprise Settings (The "Boss" Way)

This is for mandatory rules that come from the top down.
*   **How:** Administrators deploy skills through "Managed Settings."
*   **Priority:** These skills have the **Highest Priority**. They override any personal or project skills with the same name.
*   **Best For:** Compliance, security requirements, and strict company policies that *must* be followed.

## 3. The "Gotcha": Skills and Subagents

This is the most common point of confusion for beginners.

**The Rule:** Subagents **do NOT** automatically inherit your skills.
When you tell Claude to "Use a subagent" (delegate a task), that subagent starts with a **clean, empty context**. It does not know the skills you have in your main conversation.

### Two Ways to Combine Skills with Subagents

#### Approach A: Preloaded Skills in Custom Subagents

To let a custom subagent use a skill, edit its definition file (in `.claude/agents`) and add a `skills` list to the frontmatter. The full skill content is injected at startup.

```yaml
---
name: frontend-reviewer
description: Reviews frontend code...
tools: Bash, Read, WebSearch...
# You must list the skills here!
skills: accessibility-audit, performance-check
---
```

#### Approach B: Skills with `context: fork`

You can make a skill itself run in a forked subagent by adding `context: fork` to the skill's frontmatter. The skill content becomes the prompt that drives the subagent.

```yaml
---
name: deep-analysis
description: Performs deep codebase analysis...
context: fork
agent: Explore
---
```

The forked subagent won't have access to the main conversation history, but it runs independently and returns its results.

### Which Agents Can Use Skills?

1.  **Built-in Agents:** (Explorer, Plan, Verify)
    *   Cannot access skills at all. They are locked to their default behavior.
2.  **Custom Subagents:** (Agents you create)
    *   Can use skills, BUT you must explicitly list them.

### Key Difference

*   In the **Main Chat**, skills are loaded "On Demand" (when relevant).
*   In a **Subagent**, skills are loaded **at startup** (immediately when the agent launches).

## 4. Summary Checklist

*   [ ] **Project Skills:** Put them in `.claude/skills` and push to Git.
*   [ ] **Global Skills:** Use Plugins or Enterprise Settings.
*   [ ] **Subagents:** Remember that `Explorer` and `Plan` cannot use skills.
*   [ ] **Custom Agents:** Explicitly list `skills: [skill-name]` in their frontmatter if you want them to use one.

***