# Introduction to Claude Code Agent Skills

A comprehensive learning module covering Claude Code Skills — reusable Markdown-based instructions that teach Claude how to handle specific tasks automatically.

Based on [Introduction to agent skills](https://anthropic.skilljar.com/introduction-to-agent-skills), Claude Code course.

## What You'll Learn

This module covers everything from the basics of what skills are, through creating and configuring them, to advanced topics like sharing, subagent integration, and troubleshooting.

## Module Contents

| # | File | Topic | Key Concepts |
|---|------|-------|-------------|
| 1 | [001-What-are-skills.md](001-What-are-skills.md) | What are Skills? | Core concept, discovery mechanisms (semantic matching + `/` invocation), skill locations (personal, project, plugin, enterprise), hot-reload, comparison with other features |
| 2 | [002-Creating-your-first-skill.md](002-Creating-your-first-skill.md) | Creating Your First Skill | Step-by-step walkthrough building a PR description skill, `SKILL.md` structure, frontmatter, skill matching, priority hierarchy, managing skills |
| 3 | [003-Configuration-and-multi-file-skills.md](003-Configuration-and-multi-file-skills.md) | Configuration & Multi-File Skills | Complete frontmatter reference (all 10 fields), `allowed-tools` syntax, progressive disclosure pattern, scripts and token efficiency |
| 4 | [004-Skills-vs-other-Claude-Code-features.md](004-Skills-vs-other-Claude-Code-features.md) | Skills vs. Other Features | Detailed comparisons — Skills vs. CLAUDE.md, Slash Commands, Subagents, Hooks, and MCP Servers |
| 5 | [005-Sharing-skills.md](005-Sharing-skills.md) | Sharing Skills | Repository commits, plugins, enterprise settings, subagent integration (preloaded skills + `context: fork`) |
| 6 | [006-Troubleshooting-Skills.md](006-Troubleshooting-Skills.md) | Troubleshooting | Diagnostic tools, triggering issues, loading issues, conflicts, runtime errors, quick-fix checklist |

## Quick Reference

### Skill File Structure

```
~/.claude/skills/          # Personal skills (all projects)
.claude/skills/            # Project skills (this repo only)

my-skill/
├── SKILL.md               # Main instructions (required)
├── scripts/               # Executable scripts (optional)
├── references/            # Documentation files (optional)
└── assets/                # Templates, images (optional)
```

### Minimal SKILL.md

```yaml
---
name: my-skill
description: Does X when the user asks to Y or Z.
---

Instructions for Claude go here in Markdown.
```

### Frontmatter Fields at a Glance

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to directory name) |
| `description` | Recommended | What it does and when to use it (max 1,024 chars) |
| `allowed-tools` | No | Comma-separated tool whitelist (e.g., `Read, Grep, Glob`) |
| `model` | No | Model override for this skill |
| `user-invocable` | No | Set `false` to hide from `/` menu |
| `disable-model-invocation` | No | Set `true` to prevent automatic loading |
| `argument-hint` | No | Autocomplete hint (e.g., `[filename]`) |
| `context` | No | Set `fork` to run in a subagent |
| `agent` | No | Subagent type when `context: fork` |
| `hooks` | No | Lifecycle hooks scoped to this skill |

### Priority Hierarchy

```
Enterprise (highest) > Personal > Project > Plugin (lowest)
```

When skills share the same name across levels, higher-priority locations win.

## Prerequisites

- Claude Code CLI installed
- Basic familiarity with Markdown and YAML frontmatter

## Recommended Reading Order

Follow the files in numerical order (001 through 006). Each lesson builds on the previous one:

1. **Understand** what skills are and where they live
2. **Build** your first skill hands-on
3. **Configure** advanced frontmatter and multi-file patterns
4. **Compare** skills with other Claude Code customization features
5. **Share** skills with your team and integrate with subagents
6. **Troubleshoot** common issues with the diagnostic checklist
