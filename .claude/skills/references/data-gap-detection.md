# Data Gap Detection Workflow

This workflow is used by multiple skills (`trading-plan`, `trading-debate`, `position-review`, `watchlist_manager`) to identify and resolve information gaps before making decisions.

## Overview

The Data Gap Detection process uses the `ask` skill to:
1. Check question history to avoid re-asking
2. Identify missing information needed for decisions
3. Filter out self-answerable questions (use scripts, files, or web search first)
4. Present only user-only questions (personal context, judgments, preferences)
5. Track responses for future reference

## Workflow Steps

### Step 1: Check Ask History

```bash
# Read existing question history
# File: ask-history/{TICKER}.json
```

### Step 2: Identify Data Gaps

**IMPORTANT: Before asking any question, check if self-answerable:**
- Can you fetch it with a script? → Run the script
- Can you find it in analytics/news files? → Read the files
- Can you find it via web search? → Use WebSearch

**Only ask questions that are genuinely user-only.**

#### Common Data Gaps by Category

| Gap Type | Detection | Question | Self-Answerable? |
|----------|-----------|----------|------------------|
| **Missing analytics** | `analytics/{TICKER}/` not found or stale | "Run /analyze {TICKER} first" | **YES** - run `/analyze` |
| **Strategy unclear** | Analytics don't indicate strategy | "What strategy fits these technicals?" | **NO** - requires your judgment |
| **Ambiguous machine type** | Position has no machine classification | "What was original machine classification?" | **NO** - your context |
| **Missing entry rationale** | No buy reason documented | "What was original buy rationale?" | **NO** - your context |
| **Fit score impossible** | Insufficient data for fit | "What indicators suggest fit >= 60?" | **NO** - requires your judgment |
| **Missing trading levels** | No clear support/resistance | "What are key support/resistance levels?" | **YES** - check technical analysis |
| **Sector unknown** | No sector in fundamental file | "What sector and industry?" | **YES** - web search |
| **Stale fundamental data** | Analytics >7 days old | "Current fundamental score?" | **YES** - run `/analyze` |
| **Benchmark Q1: Alpha Source** | No specific edge | "What is specific competitive edge?" | Maybe - web search first |
| **Benchmark Q2: Relative Strength** | Can't determine sector comparison | "Beating sector ETF 3M?" | **YES** - calculate from price data |
| **Benchmark Q3: Institutional** | No institutional data | "Institutional ownership trend?" | **YES** - web search |
| **Benchmark Q4: Anti-Catalyst** | Unclear events | "Events in next 10 days?" | **YES** - web search earnings calendar |
| **Benchmark Q5: Sentiment** | No sentiment data | "Current social sentiment?" | **YES** - web search |
| **Insufficient catalysts** | <3 catalysts in thesis file | "Top 3 upcoming catalysts?" | **YES** - web search earnings/events |
| **Missing machine type** | No phenomenon classification | "Which machine: HYPE/EARNINGS/MEAN_REVERSION?" | **NO** - requires your judgment |
| **Low conviction** | Thesis score <60 or unclear | "What is primary bear case risk?" | Maybe - web search for risks |
| **Missing portfolio entry** | Not in portfolio.json | "Is {TICKER} in portfolio? Size?" | **YES** - check portfolio.json |
| **Unclear thesis status** | Thesis validation unknown | "Has thesis been validated?" | Maybe - check thesis file |

### Step 3: Filter Through Ask History

For each identified gap:
- **SKIP** if `status=answered` → use cached answer
- **SKIP** if `status=unavailable` AND `retry_after > NOW`
- **KEEP** if new or expired unavailable

### Step 4: Record Pending Questions

For each gap to ask:
```bash
# Use ask skill to record as pending
# - Generate unique ID
# - Set status=pending, asked_at=NOW
# - Write to ask-history/{TICKER}.json
```

### Step 5: Invoke /ask

If any gaps remain after filtering:
- Trigger `/ask {TICKER}` with pre-generated questions
- Present max 5 questions (prioritize by criticality)
- Wait for user response

### Step 6: Update History

After user responds:
```bash
# Use ask skill to update status
# - If answered: status=answered, store answer
# - If unavailable: status=unavailable, retry_after=+30d
```

## Default Values

When critical information is unavailable:

| Gap | Default Value | Notes |
|-----|---------------|-------|
| Machine type | `EARNINGS_MACHINE` | Conservative for Inertia Principle |
| Strategy | `null` | Leave unclassified |
| Fit score | `null` | Leave unclassified |

## Question Constraints

- **< 300 words** total output
- **Verifiable facts only** - no predictions/speculation
- **Categories**: fundamental, technical, catalyst, sentiment, benchmark, system
- **Max 5 questions** per invocation

## History Status Flow

```
NEW → PENDING → (answered OR unavailable)
                  ↓          ↓
               use cache   retry_after +30d
```

| Status | Action |
|--------|--------|
| `answered` | Use cached answer |
| `pending` | Awaiting response |
| `unavailable` | Re-ask after retry_after date |
