---
name: deep-research
description: Deep research on any topic using isolated Explore agent. Use for thorough codebase exploration, understanding complex systems, or comprehensive analysis. Runs in forked context for clean investigation.
argument-hint: [topic]
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Deep Research Skill

Conduct thorough, isolated research on $ARGUMENTS using the Explore agent.

## What This Does

The `context: fork` directive creates an **isolated subagent context** where:
- Only the Explore agent's read-only tools are available
- No conversation history carries over (clean slate)
- Results are summarized back to main session
- Perfect for complex investigations without clutter

## When to Use

| Use Case | Example |
|----------|---------|
| Understand codebase architecture | "How does the trading system work?" |
| Find patterns across files | "Where are portfolio calculations done?" |
| Research a topic thoroughly | "How are skills orchestrated?" |
| Explore unfamiliar areas | "What's in the analytics folder?" |
| Trace data flow | "How does price data flow through the system?" |

## How to Invoke

```
/deep-research "How does the portfolio_manager skill work?"
/deep-research "Find all files that calculate position sizing"
/deep-research "Understand the analytics generation pipeline"
```

## What You Get

The Explore agent will:
1. **Find relevant files** using Glob and Grep
2. **Read and analyze** code structure
3. **Summarize findings** with specific file references
4. **Return concise report** to main session

## Output Format

```markdown
# Research: [Topic]

## Overview
[High-level summary of findings]

## Key Files
| File | Purpose |
|------|---------|
| path/to/file | What it does |

## Patterns Discovered
- Pattern 1 with file references
- Pattern 2 with file references

## Relationships
[How components connect]

## References
- specific file:line references for all claims
```

## Why Fork Context?

Benefits of `context: fork`:
- **Isolation**: Research doesn't pollute conversation history
- **Read-only**: Can't accidentally modify files
- **Optimized tools**: Explore agent's tools tuned for codebase exploration
- **Clean slate**: No bias from previous conversation

## Constraints

- **Max 200 lines** output summary
- **Always include** file:line references
- **No tool execution** that modifies state
- **Read-only investigation** only
