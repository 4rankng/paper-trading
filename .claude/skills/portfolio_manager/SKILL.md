---
name: portfolio-manager
description: Manage portfolio holdings, execute trades, and track investment history. ALWAYS use for ANY portfolio-related query or operation. Triggers: "what is my portfolio", "show holdings", "current positions", "portfolio status", "my investments", "buy/trim/sell shares", "add/remove position", "trade history", "trade log", "recent trades", "portfolio value", "cash balance", "gain/loss", "P&L". Never directly read/write portfolio.json or trade_log.csv - use this skill instead.
allowed-tools:
  - Read
  - Bash(python:*)
---

# Portfolio Manager Skill

Manage portfolio holdings, execute trades, and track investment history with automatic cash management.

## Quick Start

```bash
# Get portfolio status
python .claude/skills/portfolio_manager/scripts/get_portfolio.py

# Execute trade (updates portfolio + trade log)
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker TCOM --action BUY --shares 84 --price 61.09 \
  --thesis-status PENDING --reasoning "Strong technical setup"

# Get trade log
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --limit 10
```

## Trade Execution Workflow

### Complete Trade Process

1. **Pre-trade analysis**: Verify signal, thesis, and risk
2. **Execute trade**: Use `update_portfolio_and_log.py`
3. **Verify**: Check portfolio state updated correctly

### Buy Workflow
```bash
# Execute buy (adds holding, deducts cash, logs trade)
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker NVDA \
  --action BUY \
  --shares 100 \
  --price 150.25 \
  --thesis-status PENDING \
  --reasoning "AI infrastructure leader, technical breakout"
```

### Sell Workflow
```bash
# Execute sell (removes holding, adds cash, logs trade)
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker LAES \
  --action SELL \
  --shares 5000 \
  --price 1.25 \
  --reasoning "Thesis failed, stop loss hit"
```

### Trim Workflow
```bash
# Execute trim (reduces position, adjusts cost basis)
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker NVDA \
  --action TRIM \
  --shares 25 \
  --price 165.00 \
  --reasoning "Take partial profits, reduce risk"
```

## Portfolio Review

```bash
# Check current state
python .claude/skills/portfolio_manager/scripts/get_portfolio.py

# Review recent trades
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --limit 20

# Filter by ticker
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --ticker NVDA
```

## File Structure

**Portfolio**: `portfolio.json` - holdings, cash, P&L, summary

**Trade Log**: `trade_log.csv` - complete trade history with reasoning

## Portfolio Management Principles

### Position Sizing Framework

Position size is determined by **expected return probability** and **risk/reward ratio**, not arbitrary percentage rules.

**Core principle:**
```
Position Size = f(Expected Return %, Probability %, Risk:Reward Ratio, Context)

Higher Expected Return → Larger Position
Higher Probability → Larger Position
Higher R:R Ratio → Larger Position
Lower R:R Ratio → Smaller Position
```

**Dynamic decision factors (no hardcoded thresholds):**
- Expected return magnitude and time horizon
- Win probability and confidence level
- Risk/reward ratio
- Cash available and opportunity cost
- Thesis quality and catalyst density
- Market conditions and volatility
- Correlation with existing holdings
- Personal risk tolerance

**The LLM agent should evaluate each opportunity holistically and size positions dynamically based on all relevant factors, not rigid formulas.**

### Selling Existing Holdings

**Only sell to free cash if:**
1. The new opportunity has **higher expected return** AND
2. The holding being sold has **lower return potential** going forward

**Never sell just for "diversification"** - concentration is acceptable if thesis is strong and expected return is high.

### Thesis Status Classification

**For evaluating whether to SELL existing positions:**
- **PENDING** - Early stage, validation required
- **VALIDATING** - Catalysts progressing, evidence accumulating
- **STRONGER** - Thesis strengthening with new evidence
- **WARNING** - Thesis at risk, monitor closely
- **DANGER** - Thesis failing or invalidated → **SELL**

**Invalidation Signals (sell triggers):**
- Partnership cancellations or failed deployments
- Regulatory setbacks that block core business
- Competitive breakthrough that negates differentiation
- Management misconduct or accounting irregularities
- Product launch failures or technological obsolescence
- Major catalysts delayed or cancelled without explanation

**NOT Invalidation (hold through):**
- Technical weakness (price below moving averages)
- Insider selling (early investors taking profits)
- Analyst downgrades (timeline extensions, not thesis breaks)
- Portfolio concentration (mechanical metric)
- Short-term volatility or sentiment swings

## Calculations

- Market Value: `shares × current_price`
- Cost Basis: Weighted average (multiple buys)
- Gain/Loss: `market_value - cost_basis`
- Portfolio %: `market_value / total_value`

## Advanced

**Complete scripts reference**: See [scripts.md](references/scripts.md) for all parameters, calculations, and data structures.

