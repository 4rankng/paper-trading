---
name: signal-formatter
description: Format trading signals with all required components. Use for: "create signal", "format buy signal", "format sell signal", "trading recommendation", "investment signal", "buy/hold/sell recommendation", "investment recommendation". Ensures signals include: action, driver class, levels, meta, risks, opportunity cost, machine logic, benchmark comparison.
---

# Signal Formatter Skill

Format trading signals with all required components.

## Quick Start

```
User: "Create a buy signal for NVDA"
→ You: Invoke signal-formatter skill
→ Use template below
→ Output: Complete formatted signal
```

## Required Components

Every signal MUST include:

### 1. Action
- BUY / SELL / HOLD / TRIM

### 2. Driver Class
- HYPE_MACHINE / EARNINGS_MACHINE / MEAN_REVERSION_MACHINE

### 3. Levels
- **Entry:** Price trigger or current price
- **Exit:** Target price or valuation trigger
- **Stop:** Loss limit (asymmetric by driver)

### 4. Meta
- **Size:** % of portfolio or dollar amount
- **Confidence:** HIGH/MEDIUM/LOW (or 1-10 scale)
- **Timeframe:** Expected holding period

### 5. Risks
Top 3 specific risks (not generic "market risk")

### 6. Opportunity Cost
What you're NOT buying to fund this trade (e.g., SPY, QQQ)

### 7. Machine Logic
Why this driver class applies to this situation

### 8. Benchmark Comparison
Use template from [benchmark-template.md](references/benchmark-template.md)

## Entry/Exit Logic by Machine

**HYPE_MACHINE:**
- Entry: Breakout + volume confirmation
- Stop: Technical breakdown (-5% or support break)

**EARNINGS_MACHINE:**
- Entry: < 80% of intrinsic value
- Stop: Fundamental degradation only (ignore price volatility)

**MEAN_REVERSION_MACHINE:**
- Entry: Fundamental strength + negative sentiment gap
- Stop: Fundamental degradation OR sentiment reversal without price follow-through

## Signal Template

```markdown
## {TICKER} Signal

**Action:** BUY/SELL/HOLD/TRIM
**Driver Class:** HYPE_MACHINE/EARNINGS_MACHINE/MEAN_REVERSION_MACHINE
**Confidence:** HIGH/MEDIUM/LOW

### Levels
- **Entry:** $XX.XX (trigger condition)
- **Exit:** $XX.XX (target condition)
- **Stop:** $XX.XX (stop condition)

### Position Sizing
- **Size:** $X,XXX or Y% of portfolio
- **Timeframe:** X months/years

### Top 3 Risks
1. [Specific risk 1]
2. [Specific risk 2]
3. [Specific risk 3]

### Opportunity Cost
Not buying: [SPY/QQQ/other ticker]
Expected alpha: Z% over benchmark

### Machine Logic
[Why this driver class applies]

### Benchmark Comparison
[Paste from benchmark-template.md]
```

## References

- [Signal Components](references/signal-components.md) - Detailed explanation of each component
- [Benchmark Template](references/benchmark-template.md) - SPY/QQQ comparison template
