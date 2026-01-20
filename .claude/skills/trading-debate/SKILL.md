---
name: trading-debate
description: Multi-agent debate framework for trading decisions with adversarial analysis. Auto-selects model by timeframe: Scalping (6 agents, 1-7d), Swing (10 agents, 1-4w), Position (7 agents, 1-6m), Investment (5 agents, 1y+). Use for: "swing trade analysis", "trading debate", "multi-agent analysis", "investment outlook".
allowed-tools:
  - Read
  - Bash(python:*)
  - Bash(ls:*)
context: fork
agent: general-purpose
---

# Trading Debate Skill

Multi-agent adversarial analysis for trading decisions. Auto-configures agent structure by timeframe.

## Quick Reference

| Timeframe | Model | Reference |
|-----------|-------|-----------|
| 1d-7d | Scalping/Day (6 agents) | [workflows.md](references/workflows.md#scalpingday-trading-model-1d---7d-4-phase-workflow) |
| 1w-4w | Swing (10 agents) | [workflows.md](references/workflows.md#swing-trading-model-1w---4w-5-phase-workflow) |
| 1m-6m | Position (7 agents) | [workflows.md](references/workflows.md#position-trading-model-1m---6m-4-phase-workflow) |
| 1y+ | Investment (5 agents) | [workflows.md](references/workflows.md#investment-model-1y-4-phase-workflow) |

## Prerequisites

**Macro Check:**
```bash
# Check current macro stance before any trading decision
ls -lt macro/theses/ | head -5
```

**Read latest macro thesis:** `macro/theses/macro_thesis_YYYY_MM.md`

Macro factors are integrated as contextual variables in all debate models.

**CRITICAL:** FRESH analytics files required (<24 hours old):
```
analytics/[TICKER]/[TICKER]_technical_analysis.md
analytics/[TICKER]/[TICKER]_fundamental_analysis.md
analytics/[TICKER]/[TICKER]_investment_thesis.md
```

**Validate:**
```bash
python .claude/skills/trading-debate/scripts/validate_analytics.py TICKER
```

If missing/stale: run `/analyze [TICKER]`

## Timeframe Format

Unit suffixes: `d` (days), `w` (weeks), `m` (months), `y` (years)

Parse: `python .claude/skills/trading-debate/scripts/parse_timeframe.py 6m`

## Reference Files

| File | Contains |
|------|----------|
| [personas.md](references/personas.md) | Persona definitions, interactions |
| [workflows.md](references/workflows.md) | Execution flows, iteration limits, monitoring |
| [constraints.md](references/constraints.md) | Veto triggers, conviction tiers, limits |
| [data-gap-detection.md](references/data-gap-detection.md) | Data validation workflow |

## When to Use

**Use for:** Trading decisions (scalping, swing, position, investment)

**NOT for:** Portfolio management (use `portfolio_manager`), existing holding reviews (use `position-review`)

## Output

**Save debate results to:** `trading-debates/[TICKER]/[TICKER]_YYYY_MM_DD_[TIMEFRAME].md`

Examples:
- `trading-debates/NVDA/NVDA_2025_01_19_2w.md`
- `trading-debates/AAPL/AAPL_2025_01_19_1y.md`

## Usage

```
/debate TICKER TIMEFRAME
```

Examples: `/debate NVDA 2w` | `/debate AAPL 1y` | `/debate TSLA 3d`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Analytics missing/stale | `/analyze TICKER` |
| Veto triggered | See [constraints.md](references/constraints.md) |
| Low conviction | Add to watchlist |
| Wrong model | Check timeframe suffix (d/w/m/y) |
