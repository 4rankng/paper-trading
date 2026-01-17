---
allowed-tools: Bash, Skill, Read, Write
description: Generate concise trading plan with entry/exit/stop and confidence level
argument-hint: [ticker] [timeframe] [capital]
---

Generate concise trading plan for [TICKER] with [TIMEFRAME] investment horizon.

**Valid Timeframes:**

| Timeframe | Approach | Position Size | Stop Loss | Target | Focus |
|-----------|----------|---------------|-----------|--------|-------|
| **1m** | Swing Trading | 0.25% max | 5-8% | 10-20% | Technicals + Short-term catalysts |
| **3m** | Position Trading | 0.5% max | 8-12% | 20-30% | Catalyst-driven |
| **6m** | Position Trading | 0.5% max | 8-12% | 20-30% | Catalyst-driven |
| **1y** | Investment | 1% max | Fundamental only | 50-100%+ | Fundamentals + Value |

**Optional:** [capital] = Total portfolio value for dollar position sizing (e.g., `/trade NVDA 3m 100000`)

## Examples
- `/trade NVDA 1m` - 1 month swing trading plan (tight stops, quick targets)
- `/trade COIN 3m` - 3 month position trading plan (catalyst-driven)
- `/trade TSLA 6m` - 6 month position trading plan (catalyst-driven)
- `/trade AAPL 1y` - 1 year investment plan (fundamental value)
- `/trade NVDA 3m 100000` - 3 month plan with $100K capital for dollar sizing

## Workflow

This command triggers the `trading-plan` skill which:

1. **Gets multi-agent insights** - Invokes trading-debate skill for adversarial analysis
2. **Reads analytics** - Loads technical, fundamental, and sentiment analysis
3. **Classifies phenomenon** - Timeframe-driven (HYPE for ≤1m/6m, EARNINGS for >1y)
4. **Runs benchmark gate** - 6 rigorous tests (≤1 fail to pass)
5. **Checks correlation** - Validates against existing portfolio holdings
6. **Generates tailored plan** - Position size, stops, targets based on timeframe
7. **Saves to file** - `trading-plans/[TICKER]/[TICKER]_YYYY_MM_DD_[TIMEFRAME].md`

## Output

**Terminal:**
- Signal (BUY/AVOID)
- Entry, Target, Stop levels
- R:R ratio and confidence
- Position size (timeframe-adjusted, with dollar amount if capital provided)
- One-line rationale

**File:**
- Complete trading plan saved to trading-plans/
- Concise format (<250 lines)
- Tailored to timeframe
- No fluff or debate

## Constraints

- For NEW BUY analysis only
- Existing holdings: Use `position-review` skill instead (Inertia Principle)
- Data freshness required: Run `/analyze [TICKER]` first if analytics missing/stale
