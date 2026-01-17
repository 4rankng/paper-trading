---
name: documentation-templates
description: Provide reference templates for manual trading plan and research documentation creation. Use for: "show trading plan template", "what's the trading plan structure", "research file format". For automated trading plan generation, use the trading-plan skill instead.
---

# Documentation Templates Skill

**Reference templates** for manual creation of trading plans and research files.

> **Note:** For automated trading plan generation with entry/exit/stop signals, use the `trading-plan` skill or `/trade [TICKER] [timeframe]` command. This skill provides template structures for reference only.

## Quick Start

```
User: "Show me the trading plan template"
→ You: Display template structure from references/
→ Output: Template sections and frontmatter

User: "What's the research file format?"
→ You: Display research-template.md structure
→ Output: Frontmatter fields and content sections
```

## Available Templates

### Trading Plan Template
**Reference structure** for 12-section trading plan.

**Location:** [trading-plan-template.md](references/trading-plan-template.md)
**Use when:** You need to understand the trading plan structure or create one manually
**For automation:** Use `trading-plan` skill or `/trade` command instead

### Research File Template
**Reference structure** for research documentation with frontmatter.

**Location:** [research-template.md](references/research-template.md)
**Use when:** Creating sector analysis, macro analysis, or industry research
**File naming:** `research/{type}-{topic}-{date}.md`

## Template Structure Overview

### Trading Plan (12 sections)
1. Executive Summary
2. Phenomenon Classification
3. Multi-Agent Debate
4. Pre-Mortem Analysis
5. Entry Benchmark Gate
6. Benchmark Comparison
7. Macro & Sector Context
8. Technical Analysis
9. Investment Strategy
10. Catalyst Timeline
11. Risk Management
12. Final Recommendation

**Full template:** [trading-plan-template.md](references/trading-plan-template.md)

### Research File (frontmatter + content)
Required frontmatter fields:
- title, type, topic, tags
- created, updated
- related_stocks, related_sectors
- importance, status
- machine_context, catalyst_type

**Full template:** [research-template.md](references/research-template.md)

## References

- [Trading Plan Template](references/trading-plan-template.md) - Full 126-line template
- [Research Template](references/research-template.md) - Frontmatter + structure
- [Examples](references/examples/) - Real trading plans for reference
