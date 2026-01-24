## Custom Slash Commands

Custom slash commands allow you to define frequently used prompts as Markdown files that Claude Code can execute. Commands are organized by scope (project-specific or personal) and support namespacing through directory structures.

### Syntax

```
/<command-name> [arguments]
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `<command-name>` | Name derived from the Markdown filename (without `.md` extension) |
| `[arguments]` | Optional arguments passed to the command |

### Project Commands

Commands stored in your repository and shared with your team. When listed in `/help`, these commands show "(project)" after their description.

**Location:** `.claude/commands/`

The following example creates the `/optimize` command:

```bash
# Create a project command
mkdir -p .claude/commands
echo "Analyze this code for performance issues and suggest optimizations:" > .claude/commands/optimize.md
```

### Personal Commands

Commands available across all your projects. When listed in `/help`, these commands show "(user)" after their description.

**Location:** `~/.claude/commands/`

The following example creates the `/security-review` command:

```bash
# Create a personal command
mkdir -p ~/.claude/commands
echo "Review this code for security vulnerabilities:" > ~/.claude/commands/security-review.md
```

### Features

#### Namespacing

Use subdirectories to group related commands. Subdirectories appear in the command description but don't affect the command name.

**For example:**
- `.claude/commands/frontend/component.md` creates `/component` with description "(project:frontend)"
- `~/.claude/commands/component.md` creates `/component` with description "(user)"

**Priority Rules:**
- If a project command and user command share the same name, the project command takes precedence and the user command is silently ignored
- Commands in different subdirectories can share names since the subdirectory appears in the description to distinguish them
- Example: `.claude/commands/frontend/test.md` and `.claude/commands/backend/test.md` both create `/test`, but show as "(project:frontend)" and "(project:backend)" respectively

#### Arguments

Pass dynamic values to commands using argument placeholders:

##### All arguments with `$ARGUMENTS`

The `$ARGUMENTS` placeholder captures all arguments passed to the command:

```bash
# Command definition
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# Usage
> /fix-issue 123 high-priority
# $ARGUMENTS becomes: "123 high-priority"
```

##### Individual arguments with `$1`, `$2`, etc.

Access specific arguments individually using positional parameters (similar to shell scripts):

```bash
# Command definition
echo 'Review PR #$1 with priority $2 and assign to $3' > .claude/commands/review-pr.md

# Usage
> /review-pr 456 high alice
# $1 becomes "456", $2 becomes "high", $3 becomes "alice"
```

**Use positional arguments when you need to:**
- Access arguments individually in different parts of your command
- Provide defaults for missing arguments
- Build more structured commands with specific parameter roles

#### Bash Command Execution

Execute bash commands before the slash command runs using the `!` prefix. The output is included in the command context. You **must** include `allowed-tools` with the Bash tool, but you can choose the specific bash commands to allow.

```yaml
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create a single git commit.
```
