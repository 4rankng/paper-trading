---
name: debate
description: Multi-agent debate framework for current affairs and macroeconomic analysis. Auto-selects personas by topic: Geopolitics (6 agents), Economics (8 agents), Policy (7 agents), Markets (5 agents). Use for: "debate tariffs", "analyze fed policy", "geopolitical analysis", "macro outlook".
allowed-tools:
  - Read
  - Bash(python:*)
  - Bash(ls:*)
  - mcp__web-search-prime__webSearchPrime
  - mcp__web-reader__webReader
  - mcp__reddit__fetch_reddit_hot_threads
  - mcp__memory__*
context: fork
agent: general-purpose
---

# Debate Skill

Multi-agent adversarial analysis for current affairs, macroeconomics, and policy decisions. Auto-configures agent structure by topic.

## Quick Reference

| Topic | Model | Agents | Reference |
|-------|-------|--------|-----------|
| Geopolitics | Diplomacy/Security (6 agents) | [personas.md](references/personas.md#geopolitics-model) | [workflows.md](references/workflows.md) |
| Economics | Macro Analysis (8 agents) | [personas.md](references/personas.md#economics-model) | [workflows.md](references/workflows.md) |
| Policy | Domestic/International (7 agents) | [personas.md](references/personas.md#policy-model) | [workflows.md](references/workflows.md) |
| Markets | Macro Market View (5 agents) | [personas.md](references/personas.md#markets-model) | [workflows.md](references/workflows.md) |

## Prerequisites

**Macro Check:**
```bash
# Check current macro stance before any debate
ls -lt macro/theses/ | head -5
```

**Read latest macro thesis:** `macro/theses/macro_thesis_YYYY_MM.md`

**Data Gathering (for time-sensitive topics):**
```bash
# Use WebSearch for latest news on the topic
# Use WebReader to read detailed articles
# Use Reddit to gauge public sentiment
```

## Reference Files

| File | Contains |
|------|----------|
| [personas.md](references/personas.md) | Persona definitions, perspectives, biases |
| [workflows.md](references/workflows.md) | Execution flows, iteration limits, synthesis |
| [constraints.md](references/constraints.md) | Factual accuracy requirements, source standards |

## When to Use

**Use for:**
- Geopolitical events (wars, trade disputes, diplomatic tensions)
- Macroeconomic analysis (Fed policy, inflation, GDP, employment)
- Policy decisions (elections, legislation, regulations)
- Current affairs with market implications

**NOT for:** Trading decisions (use `trading-debate`), portfolio management (use `portfolio_manager`)

## Output

**Save debate results to:** `debates/[TOPIC]/[TOPIC]_YYYY_MM_DD.md`

Examples:
- `debates/us_eu_tariffs/us_eu_tariffs_2026_01_20.md`
- `debates/fed_rate_decision/fed_rate_decision_2026_01_20.md`

## Usage

```
/debate [TOPIC]
```

Examples:
- `/debate Should the Fed cut rates in January?`
- `/debate Will US-EU trade war escalate?`
- `/debate Impact of AI on employment`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Insufficient current data | Use WebSearch/WebReader to gather latest info |
| Low confidence | Add to macro/ overview for later review |
| Conflicting sources | Document all sources with credibility assessment |

## Persona Clusters

| Cluster | Purpose |
|---------|---------|
| Historical Context | Past precedents, pattern recognition |
| Economic Analysis | Data-driven impact assessment |
| Strategic Foresight | Scenario planning, probability analysis |
| Social Impact | Public sentiment, political feasibility |
| Synthesis | Final recommendation with confidence level |
