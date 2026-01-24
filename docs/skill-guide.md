# Complete Guide to Creating Claude Code Skills

## Table of Contents

- [How Skills Work](#how-skills-work)
- [Where Skills Live](#where-skills-live)
- [When to Use Skills Versus Other Options](#when-to-use-skills-versus-other-options)
- [Configure Skills](#configure-skills)
  - [Write SKILL.md](#write-skillmd)
  - [Update or Delete a Skill](#update-or-delete-a-skill)
  - [Add Supporting Files with Progressive Disclosure](#add-supporting-files-with-progressive-disclosure)
  - [Restrict Tool Access with allowed-tools](#restrict-tool-access-with-allowed-tools)
  - [Run Skills in a Forked Context](#run-skills-in-a-forked-context)
  - [Define Hooks for Skills](#define-hooks-for-skills)
  - [Control Skill Visibility](#control-skill-visibility)
  - [Skills and Subagents](#skills-and-subagents)
  - [Distribute Skills](#distribute-skills)
- [Examples](#examples)
  - [Simple Skill (Single File)](#simple-skill-single-file)
  - [Use Multiple Files]((#use-multiple-files)
- [Troubleshooting](#troubleshooting)

---

## How Skills Work

A Skill is a markdown file that teaches Claude how to do something specific: reviewing PRs using your team's standards, generating commit messages in your preferred format, or querying your company's database schema. When you ask Claude something that matches a Skill's purpose, Claude automatically applies it.

Skills are **model-invoked**: Claude decides which Skills to use based on your request. You don't need to explicitly call a Skill. Claude automatically applies relevant Skills when your request matches their description.

When you send a request, Claude follows these steps to find and use relevant Skills:
1. **Discovery** - At startup, Claude loads only the name and description of each available Skill
2. **Activation** - When your request matches a Skill's description, Claude loads the full SKILL.md
3. **Execution** - Claude follows the Skill's instructions, loading referenced files or running bundled scripts as needed

---

## Where Skills Live

Where you store a Skill determines who can use it:

| Location | Path | Applies To |
|----------|------|------------|
| **Enterprise** | See managed settings | All users in your organization |
| **Personal** | `~/.claude/skills/` | You, across all your projects |
| **Project** | `.claude/skills/` | Anyone working in this repository |
| **Plugin** | Bundled with plugins | Anyone with the plugin installed |

If two Skills have the same name, the higher row wins: managed overrides personal, personal overrides project, and project overrides plugin.

### Automatic Discovery from Nested Directories

When you work with files in subdirectories, Claude Code automatically discovers Skills from nested `.claude/skills/` directories. For example, if you're editing a file in `packages/frontend/`, Claude Code also looks for Skills in `packages/frontend/.claude/skills/`. This supports monorepo setups where packages have their own Skills.

---

## When to Use Skills Versus Other Options

Claude Code offers several ways to customize behavior. The key difference: **Skills are triggered automatically by Claude** based on your request, while slash commands require you to type `/command` explicitly.

| Use this | When you want to… | When it runs |
|--------|------------------|--------------|
| **Skills** | Give Claude specialized knowledge (e.g., "review PRs using our standards") | Claude chooses when relevant |
| **Slash commands** | Create reusable prompts (e.g., `/deploy staging`) | You type `/command` to run it |
| **CLAUDE.md** | Set project-wide instructions (e.g., "use TypeScript strict mode") | Loaded into every conversation |
| **Subagents** | Delegate tasks to a separate context with its own tools | Claude delegates, or you invoke explicitly |
| **Hooks** | Run scripts on events (e.g., lint on file save) | Fires on specific tool events |
| **MCP servers** | Connect Claude to external tools and data sources | Claude calls MCP tools as needed |

**Skills vs. subagents:** Skills add knowledge to the current conversation. Subagents run in a separate context with their own tools. Use Skills for guidance and standards; use subagents when you need isolation or different tool access.

**Skills vs. MCP:** Skills tell Claude _how_ to use tools; MCP _provides_ the tools. For example, an MCP server connects Claude to your database, while a Skill teaches Claude your data model and query patterns.

---

## Configure Skills

This section covers Skill file structure, supporting files, tool restrictions, and distribution options.

### Write SKILL.md

The `SKILL.md` file is the only required file in a Skill. It has two parts: YAML metadata (the section between `---` markers) at the top, and Markdown instructions that tell Claude how to use the Skill:

```
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
```

#### Available Metadata Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill name. Must use lowercase letters, numbers, and hyphens only (max 64 characters). Should match the directory name. |
| `description` | Yes | What the Skill does and when to use it (max 1024 characters). Claude uses this to decide when to apply the Skill. |
| `allowed-tools` | No | Tools Claude can use without asking permission when this Skill is active. Supports comma-separated values or YAML-style lists. |
| `model` | No | Model to use when this Skill is active (e.g., `claude-sonnet-4-20250514`). Defaults to the conversation's model. |
| `context` | No | Set to `fork` to run the Skill in a forked sub-agent context with its own conversation history. |
| `agent` | No | Specify which agent type to use when `context: fork` is set (e.g., `Explore`, `Plan`, `general-purpose`, or a custom agent name from `.claude/agents/`). Defaults to `general-purpose` if not specified. Only applicable when combined with `context: fork`. |
| `hooks` | No | Define hooks scoped to this Skill's lifecycle. Supports `PreToolUse`, `PostToolUse`, and `Stop` events. |
| `user-invocable` | No | Controls whether the Skill appears in the slash command menu. Does not affect the `Skill` tool or automatic discovery. Defaults to `true`. |

#### Available String Substitutions

Skills support string substitution for dynamic values in the Skill content:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the Skill. If `$ARGUMENTS` is not present in the content, arguments are appended as `ARGUMENTS: <value>`. |
| `${CLAUDE_SESSION_ID}` | The current session ID. Useful for logging, creating session-specific files, or correlating Skill output with sessions. |

**Example using substitutions:**

```
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

### Update or Delete a Skill

To update a Skill, edit its `SKILL.md` file directly. To remove a Skill, delete its directory. Changes take effect immediately.

### Add Supporting Files with Progressive Disclosure

Skills share Claude's context window with conversation history, other Skills, and your request. To keep context focused, use **progressive disclosure**: put essential information in `SKILL.md` and detailed reference material in separate files that Claude reads only when needed.

This approach lets you bundle comprehensive documentation, examples, and scripts without consuming context upfront. Claude loads additional files only when the task requires them.

#### Example: Multi-File Skill Structure

Claude discovers supporting files through links in your `SKILL.md`. The following example shows a Skill with detailed documentation in separate files and utility scripts that Claude can execute without reading:

```
my-skill/
├── SKILL.md              (required - overview and navigation)
├── reference.md          (detailed API docs - loaded when needed)
├── examples.md           (usage examples - loaded when needed)
└── scripts/
    └── helper.py         (utility script - executed, not loaded)
```

The `SKILL.md` file references these supporting files so Claude knows they exist:

```markdown
## Overview

[E essential instructions here]

## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)

## Utility scripts

To validate input files, run the helper script. It checks for required fields and returns any validation errors:

```bash
python scripts/helper.py input.txt
```
```

**Bundle utility scripts for zero-context execution.** Scripts in your Skill directory can be executed without loading their contents into context. Claude runs the script and only the output consumes tokens. This is useful for:

- Complex validation logic that would be verbose to describe in prose
- Data processing that's more reliable as tested code than generated code
- Operations that benefit from consistency across uses

In `SKILL.md`, tell Claude to run the script rather than read it:

```markdown
Run the validation script to check the form:
```bash
python scripts/validate_form.py input.pdf
```
```

### Restrict Tool Access with allowed-tools

Use the `allowed-tools` frontmatter field to limit which tools Claude can use when a Skill is active. You can specify tools as a comma-separated string or a YAML list:

**Comma-separated format:**

```
---
name: reading-files-safely
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---
```

**YAML list format:**

```
---
name: reading-files-safely
description: Read files without making changes. Use when you need read-only file access.
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

When this Skill is active, Claude can only use the specified tools (Read, Grep, Glob) without needing to ask for permission. This is useful for:

- Read-only Skills that shouldn't modify files
- Skills with limited scope: for example, only data analysis, no file writing
- Security-sensitive workflows where you want to restrict capabilities

If `allowed-tools` is omitted, the Skill doesn't restrict tools. Claude uses its standard permission model and may ask you to approve tool usage.

### Run Skills in a Forked Context

Use `context: fork` to run a Skill in an isolated sub-agent context with its own conversation history. This is useful for Skills that perform complex multi-step operations without cluttering the main conversation:

```
---
name: code-analysis
description: Analyze code quality and generate detailed reports
context: fork
---
```

### Define Hooks for Skills

Skills can define hooks that run during the Skill's lifecycle. Use the `hooks` field to specify `PreToolUse`, `PostToolUse`, or `Stop` handlers:

```
---
name: secure-operations
description: Perform operations with additional security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh $TOOL_INPUT"
          once: true
---
```

The `once: true` option runs the hook only once per session. After the first successful execution, the hook is removed.

Hooks defined in a Skill are scoped to that Skill's execution and are automatically cleaned up when the Skill finishes.

### Control Skill Visibility

Skills can be invoked in three ways:

1. **Manual invocation**: You type `/skill-name` in the prompt
2. **Programmatic invocation**: Claude calls it via the `Skill` tool
3. **Automatic discovery**: Claude reads the Skill's description and loads it when relevant to the conversation

The `user-invocable` field controls only manual invocation. When set to `false`, the Skill is hidden from the slash command menu but Claude can still invoke it programmatically or discover it automatically. To block programmatic invocation via the `Skill` tool, use `disable-model-invocation: true` instead.

#### When to Use Each Setting

| Setting | Slash menu | `Skill` tool | Auto-discovery | Use case |
|---------|------------|-------------|----------------|----------|
| `user-invocable: true` (default) | Visible | Allowed | Yes | Skills you want users to invoke directly |
| `user-invocable: false` | Hidden | Allowed | Yes | Skills that Claude can use but users shouldn't invoke manually |
| `disable-model-invocation: true` | Visible | Blocked | Yes | Skills you want users to invoke but not Claude programmatically |

#### Example: Model-Only Skill

Set `user-invocable: false` to hide a Skill from the slash menu while still allowing Claude to invoke it programmatically:

```
---
name: internal-review-standards
description: Apply internal code review standards when reviewing pull requests
user-invocable: false
---
```

With this setting, users won't see the Skill in the `/` menu, but Claude can still invoke it via the `Skill` tool or discover it automatically based on context.

### Skills and Subagents

There are two ways Skills and subagents can work together:

#### Give a Subagent Access to Skills

Subagents do **not** automatically inherit Skills from the main conversation. To give a custom subagent access to specific Skills, list them in the subagent's `skills` field:

```markdown
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Review code for quality and best practices
skills: pr-review, security-check
---
```

The full content of each listed Skill is injected into the subagent's context at startup, not just made available for invocation. If the `skills` field is omitted, no Skills are loaded for that subagent.

**Built-in agents** (Explore, Plan, general-purpose) do **not** have access to your Skills. Only custom subagents you define in `.claude/agents/` with an explicit `skills` field can use Skills.

#### Run a Skill in a Subagent Context

Use `context: fork` and `agent` to run a Skill in a forked subagent with its own separate context. See [Run Skills in a Forked Context](#run-skills-in-a-forked-context) for details.

### Distribute Skills

You can share Skills in several ways:

- **Project Skills**: Commit `.claude/skills/` to version control. Anyone who clones the repository gets the Skills.
- **Plugins**: To share Skills across multiple repositories, create a `skills/` directory in your plugin with Skill folders containing `SKILL.md` files. Distribute through a plugin marketplace.
- **Managed**: Administrators can deploy Skills organization-wide through managed settings. See [Where Skills Live](#where-skills-live) for managed Skill paths.

---

## Examples

These examples show common Skill patterns, from minimal single-file Skills to multi-file Skills with supporting documentation and scripts.

### Simple Skill (Single File)

A minimal Skill needs only a `SKILL.md` file with frontmatter and instructions. This example helps Claude generate commit messages by examining staged changes:

**Structure:**
```
commit-helper/
└── SKILL.md
```

**SKILL.md:**
```
---
name: generating-commit-messages
description: Generates clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.
---

# Generating Commit Messages

## Instructions

1. Run `git diff --staged` to see changes
2. I'll suggest a commit message with:
   - Summary under 50 characters
   - Detailed description
   - Affected components

## Best practices

- Use present tense
- Explain what and why, not how
```

### Use Multiple Files

For complex Skills, use progressive disclosure to keep the main `SKILL.md` focused while providing detailed documentation in supporting files. This PDF processing Skill includes reference docs, utility scripts, and uses `allowed-tools` to restrict Claude to specific tools:

**Structure:**
```
pdf-processing/
├── SKILL.md              # Overview and quick start
├── FORMS.md              # Form field mappings and filling instructions
├── REFERENCE.md          # API details for pypdf and pdfplumber
└── scripts/
    ├── fill_form.py      # Utility to populate form fields
    └── validate.py       # Checks PDFs for required fields
```

**SKILL.md:**
```
---
name: pdf-processing
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber packages.
allowed-tools: Read, Bash(python:*)
---

# PDF Processing

## Quick start

Extract text:
```python
import pdfplumber
with pdfplumber.open("doc.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For form filling, see [FORMS.md](FORMS.md).
For detailed API reference, see [REFERENCE.md](REFERENCE.md).

## Requirements

Packages must be installed in your environment:
```bash
pip install pypdf pdfplumber
```
```

---

## Troubleshooting

### View and Test Skills

To see which Skills Claude has access to, ask Claude a question like "What Skills are available?" Claude loads all available Skill names and descriptions into the context window when a conversation starts, so it can list the Skills it currently has access to.

To test a specific Skill, ask Claude to do a task that matches the Skill's description. For example, if your Skill has the description "Reviews pull requests for code quality", ask Claude to "Review the changes in my current branch." Claude automatically uses the Skill when the request matches its description.

### Skill Not Triggering

The description field is how Claude decides whether to use your Skill. Vague descriptions like "Helps with documents" don't give Claude enough information to match your Skill to relevant requests.

A good description answers two questions:

1. **What does this Skill do?** List the specific capabilities.
2. **When should Claude use it?** Include trigger terms users would mention.

```
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

This description works because it names specific actions (extract, fill, merge) and includes keywords users would say (PDF, forms, document extraction).

### Skill Doesn't Load

**Check the file path.** Skills must be in the correct directory with the exact filename `SKILL.md` (case-sensitive):

| Type | Path |
|------|------|
| Personal | `~/.claude/skills/my-skill/SKILL.md` |
| Project | `.claude/skills/my-skill/SKILL.md` |
| Enterprise | See [Where Skills Live](#where-skills-live) for platform-specific paths |
| Plugin | `skills/my-skill/SKILL.md` inside the plugin directory |

**Check the YAML syntax.** Invalid YAML in the frontmatter prevents the Skill from loading. The frontmatter must:
- Start with `---` on line 1 (no blank lines before it)
- End with `---` before the Markdown content
- Use spaces for indentation (not tabs)

**Run debug mode.** Use `claude --debug` to see Skill loading errors.

### Skill Has Errors

**Check dependencies are installed.** If your Skill uses external packages, they must be installed in your environment before Claude can use them.

**Check script permissions.** Scripts need execute permissions:
```bash
chmod +x scripts/*.py
```

**Check file paths.** Use forward slashes (Unix style) in all paths. Use `scripts/helper.py`, not `scripts\\helper.py`.

### Multiple Skills Conflict

If Claude uses the wrong Skill or seems confused between similar Skills, the descriptions are probably too similar. Make each description distinct by using specific trigger terms.

For example, instead of two Skills with "data analysis" in both descriptions, differentiate them: one for "sales data in Excel files and CRM exports" and another for "log files and system metrics". The more specific your trigger terms, the easier it is for Claude to match the right Skill to your request.

### Plugin Skills Not Appearing

**Symptom:** You installed a plugin from a marketplace, but its Skills don't appear when you ask Claude "What Skills are available?"

**Solution:** Clear the plugin cache and reinstall:

```bash
rm -rf ~/.claude/plugins/cache
```

Then restart Claude Code and reinstall the plugin:

```
/plugin install plugin-name@marketplace-name
```

This forces Claude Code to re-download and re-register the plugin's Skills.

**If Skills still don't appear**, verify the plugin's directory structure is correct. Skills must be in a `skills/` directory at the plugin root:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── my-skill/
        └── SKILL.md
```

---

## Best Practices Summary

When creating Skills:

- **Write clear, specific descriptions** - Include both what the Skill does and when to trigger it
- **Use progressive disclosure** - Keep SKILL.md concise (<500 lines), move details to reference files
- **Bundle utility scripts** - Execute scripts without loading them into context for zero-token-cost operations
- **Test Skills thoroughly** - Verify they trigger with natural language requests
- **Organize by domain** - Group related functionality in focused Skills
- **Use allowed-tools** - Restrict tool access for read-only or security-sensitive workflows
- **Consider subagent context** - Use `context: fork` for complex multi-step operations

Remember: Skills are orchestrators, not tools themselves. They guide Claude on how to use actual tools, APIs, and data to accomplish specialized tasks effectively.
