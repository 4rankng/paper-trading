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

## Thesis Status

Track validation progress: PENDING → VALIDATING → VALIDATED (or FAILED/TRANSFORMING/INVALIDATED)

## Calculations

- Market Value: `shares × current_price`
- Cost Basis: Weighted average (multiple buys)
- Gain/Loss: `market_value - cost_basis`
- Portfolio %: `market_value / total_value`

## Advanced

**Complete scripts reference**: See [scripts.md](references/scripts.md) for all parameters, calculations, and data structures.

