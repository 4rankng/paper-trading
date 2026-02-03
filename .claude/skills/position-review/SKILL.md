---
name: position-review
description: Review existing portfolio holdings for exit/hold decisions. Use for: "should I sell [TICKER]", "analyze my [TICKER] position", "review portfolio", "update on [TICKER]", "what about my holdings", "position analysis", "exit decision". DO NOT use for new buy analysis (use investment-workflow skill instead). Applies Inertia Principle: existing positions VALID unless proven DEAD. Supports multi-portfolio: specify --portfolio to target specific portfolio.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
---

# Position Review Skill

Review existing holdings using Inertia Principle and machine-specific exit logic.

## Multi-Portfolio Support

When reviewing positions, specify which portfolio to review:

```bash
# Get holdings from specific portfolio
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --portfolio CORE

# List all portfolios
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --list
```

If no portfolio is specified, the default portfolio from `metadata.default_portfolio` is used.

## Core Principle: Inertia

**Existing positions = VALID unless proven DEAD**

- Fundamentals intact → Price volatility/size/benchmarks irrelevant
- Burden: System must PROVE thesis is DEAD to sell
- NEVER sell EARNINGS_MACHINE for price drop or technical breakdown

## Quick Start

```
User: "Should I sell my AAPL position in CORE portfolio?"
→ Get holdings from CORE portfolio
→ Follow 3-step process below
→ Output: HOLD/SELL/TRIM decision
```

## Data Gap Detection (Before Classification)

**Before starting position review, check for data gaps using the `ask` skill.**

See [Data Gap Detection Workflow](references/data-gap-detection.md) for the complete process.

**Priority gaps for position-review:** Ambiguous machine type, missing entry rationale, unclear thesis status.

**If machine type is unavailable**, default to EARNINGS_MACHINE (conservative for Inertia Principle).

## Fresh Data Check (MANDATORY BEFORE REVIEW)

Before ANY position review, you MUST follow the 3-step checklist:
**[Data-First Decision Making](references/data-first-decision-making.md)**

## Macro Risk Check

**Before thesis validation, read latest macro thesis:** `macro/theses/macro_thesis_YYYY_MM.md`

**Macro factors that can invalidate a thesis:**
- **Recession onset:** Consumer discretionary, cyclicals may weaken despite strong fundamentals
- **Interest rate shocks:** High-debt companies, REITs, growth stocks face headwinds
- **Geopolitical escalation:** Supply chain disruptions, commodity price spikes
- **Sector-specific regulations:** Policy changes that materially affect business model

**If macro factor is thesis-critical:** Consider downgrade to WARNING status even if company fundamentals remain intact.

---

## 3-Step Position Review

### Step 1: Classify Machine Type

Determine if position is:
- **HYPE_MACHINE** (sentiment-driven trading position)
- **EARNINGS_MACHINE** (fundamental-driven investment)
- **MEAN_REVERSION_MACHINE** (Graham gap arbitrage)

See [machine-classifications.md](references/machine-classifications.md) for guidance.

### Step 2: Check Thesis Validation

**Read Analytics Files:**
- `analytics/{TICKER}/{TICKER}_investment_thesis.md` - Thesis status, validation milestones
- `analytics/{TICKER}/{TICKER}_technical_analysis.md` - Technical score, key levels
- `analytics/{TICKER}/{TICKER}_fundamental_analysis.md` - Fundamental score, business health

**Check Validation Milestones:**
- Bullish signals confirmed? (3/8+ = working)
- Bearish signals triggered? (Any = thesis failing)
- Fundamental score < 50? → Consider exit
- Thesis invalidated? → Exit immediately

**Apply Exit Logic:**

**HYPE_MACHINE:**
- Price below technical support? → SELL/TRIM
- Momentum score drops significantly? → SELL/TRIM
- Otherwise → HOLD

**EARNINGS_MACHINE or MEAN_REVERSION_MACHINE:**
- Fundamental Score < 50 OR Thesis invalidated? → SELL
- Fundamentals stable → Go to Step 3

See [exit-logic-by-machine.md](references/exit-logic-by-machine.md) for detailed rules.

### Step 3: Fear Check

Price dropping due to fear/volatility?
- **YES** → DO NOT SELL. Consider ADDING.
- **NO (Overvaluation)** → TRIM (optional)

## ⛔ EXPLICITLY FORBIDDEN

- Checking Position Size
- Running Benchmark Gate Tests
- Checking Technical Support (unless selling for cash reasons)

## Output Format

Use `signal-formatter` Skill to create properly formatted exit signal.

## References

- [Exit Logic by Machine](references/exit-logic-by-machine.md) - Detailed exit rules for each machine type
- [Machine Classifications](references/machine-classifications.md) - How to classify positions
