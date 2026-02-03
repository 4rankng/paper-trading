---
name: skill-manager
description: Meta-skill to list, validate, and manage other skills. Use this to discover available skills and their capabilities.
allowed-tools:
  - Read
  - Bash(python:*)
---

# Skill Manager

Manage and discover skills in the `.claude/skills` directory.

## Quick Start

```bash
# List all available skills and their descriptions
python .claude/skills/skill_manager/scripts/list_skills.py

# Validate skill structure (dev tool)
python .claude/skills/skill_manager/scripts/validate_skills.py
```

## Available Scripts

- `list_skills.py`: Scans `.claude/skills` and prints a summary table of skills and their descriptions from `SKILL.md` frontmatter.
- `validate_skills.py`: Checks if skills follow the standard structure (SKILL.md, scripts folder, etc.).
