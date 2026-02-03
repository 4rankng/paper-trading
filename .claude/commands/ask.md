---
name: ask
description: Generate 5 factual questions about a ticker with intelligent history tracking to avoid duplicates. Auto-triggered by decision skills when data gaps detected.
argument-hint: [ticker]
disable-model-invocation: true
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
  - Skill(ask)
  - Skill(analytics_generator)
---

Use the `ask` skill to generate questions about {TICKER}.

**DO NOT ASK - handled by other skills:**
| Question Type | Use Skill Instead |
|---------------|-------------------|
| Position status, holding, exit/entry decisions | `portfolio_manager` |
| Timeframe (scalping/position/investment) | `portfolio_manager` |
| Personal investment rationale/conviction | `portfolio_manager` |
| Target price/stop loss preferences | `portfolio_manager` |
| Competitive analysis, bear/bull cases | `trading-debate` |
| Hold/sell decision on existing position | `position-review` |

**ONLY ASK:**
- Publicly verifiable facts NOT found via web search
- Data gaps preventing analytics generation
- Information not in `analytics/{TICKER}/`, `news/{TICKER}/`, or via `WebSearch`

**Invoke:** `Skill` with `ask`
