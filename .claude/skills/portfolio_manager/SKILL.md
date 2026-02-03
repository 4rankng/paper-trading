---
name: portfolio-manager
description: Manage portfolio holdings, execute trades, and track investment history. ALWAYS use for ANY portfolio-related query or operation. Triggers: "what is my portfolio", "show holdings", "current positions", "portfolio status", "my investments", "buy/trim/sell shares", "add/remove position", "trade history", "trade log", "recent trades", "portfolio value", "cash balance", "gain/loss", "P&L". Never directly read/write portfolios.json or trade_log.csv - use this skill instead.
allowed-tools:
  - Read
  - Bash(python:*)
---

# Portfolio Manager Skill

Manage portfolio holdings, execute trades, and track investment history.

## Multi-Portfolio Architecture (v3.0 Minimal)

**CRITICAL:** `portfolios.json` stores ONLY minimal position data. All analysis data (thesis, sector, machine_type, etc.) MUST be stored in `analytics/[TICKER]/` folder.

**Shared Cash Pool:** All portfolios share a single cash pool at `portfolios.json` root.
- Portfolios contain only stock positions (holdings)
- Position % = `position_value / (holdings_value + shared_cash)`
- Trading from any portfolio affects the shared cash pool

### Minimal portfolios.json Structure

```json
{
  "cash": {"amount": 1000.00, "target_buffer_pct": 15},
  "portfolios": {
    "CORE": {
      "name": "Core Holdings",
      "description": "...",
      "config": {...},
      "holdings": [
        {
          "ticker": "TICKER",
          "shares": 100,
          "avg_cost": 10.50,
          "current_price": 12.00,
          "status": "active"
        }
      ],
      "summary": {...}
    }
  },
  "metadata": {"default_portfolio": "CORE", "version": "3.0"}
}
```

**Allowed fields in holdings:** `ticker`, `shares`, `avg_cost`, `current_price`, `status`
**Calculated fields (runtime):** `market_value`, `gain_loss`, `gain_loss_pct`, `pct_portfolio`

**Analysis data lives in:** `analytics/[TICKER]/`
- `{TICKER}_investment_thesis.md`
- `{TICKER}_technical_analysis.md`
- `{TICKER}_fundamental_analysis.md`
- `price.csv` (historical prices)

## Quick Start

```bash
# List all portfolios
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --list

# Get default portfolio status
python .claude/skills/portfolio_manager/scripts/get_portfolio.py

# Get status (minimal data only - use analytics_generator for analysis)
python .claude/skills/portfolio_manager/scripts/get_portfolio.py

# Get specific portfolio status
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --portfolio AI_PICKS

# Execute trade in default portfolio
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker TCOM --action BUY --shares 84 --price 61.09 \
  --reasoning "Strong technical setup"

# Execute trade in specific portfolio
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker TCOM --action BUY --shares 84 --price 61.09 --portfolio CORE \
  --reasoning "Strong technical setup"

# Get trade log
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --limit 10
```

## File Structure

- **portfolios.json** - Multi-portfolio with shared cash pool (MINIMAL DATA ONLY)
- **trade_log.csv** - Complete trade history with `portfolio` column
- **analytics/[TICKER]/** - Analysis files (thesis, technical, fundamental)

## Buy Score Quick Reference

| Score | Action |
|-------|--------|
| 75+ | Strong Buy |
| 60-74 | Buy |
| 50-59 | Moderate Buy (WATCH) |
| <50 | Weak/Avoid |

**Formula:** `Buy Score = (Thesis × 0.35) + (Fundamental × 0.25) + (R:R × 0.15) + (Technical × 0.15) + (Volume × 0.10)`

**Detailed methodology:** See [buy_score_guide.md](references/buy_score_guide.md)

## Portfolio Management Principles

### Position Sizing

```
Position Size = f(Expected Return %, Probability %, Risk:Reward Ratio, Context)

Higher Expected Return → Larger Position
Higher Probability → Larger Position
Higher R:R Ratio → Larger Position
```

Evaluate holistically, no hardcoded thresholds.

### Selling Existing Holdings

**Only sell to free cash if:**
1. The new opportunity has **higher expected return** AND
2. The holding being sold has **lower return potential** going forward

**Never sell just for "diversification"** - concentration is acceptable if thesis is strong.

## Concentration & Conviction

**CRITICAL: Do NOT give cookie-cutter concentration warnings.**

When concentration is JUSTIFIED:
- Strong thesis with 80%+ conviction
- Asymmetric upside (3-10x potential vs -50% risk)
- Catalysts validated (not hypothetical)
- You've done the work

**Rule: If thesis is STRONG and UPSIDE is ASYMMETRIC, concentration is POWER.**

Concentration risk is only relevant when conviction is low or thesis is weak. High conviction justifies high concentration.

### Thesis Status Classification

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Early stage, validation required | Monitor |
| VALIDATING | Catalysts progressing, evidence accumulating | Hold/Add |
| STRONGER | Thesis strengthening with new evidence | Hold/Add |
| WARNING | Thesis at risk, monitor closely | Reduce exposure |
| DANGER | Thesis failing or invalidated | **SELL** |
| FAILED | Thesis failed, catalyst didn't materialize | **EXIT** |
| INVALIDATED | Thesis invalidated by events | **EXIT IMMEDIATELY** |

## Phenomenon Classifications

**NEVER use "SPECIAL_SITUATION" as a classification** - it is meaningless. Use precise, descriptive names.

| Phenomenon | When to Use | Example |
|------------|-------------|---------|
| **MEAN_REVERSION** | Oversold, -30%+ off highs, contrarian setup | CVLT |
| **EARNINGS_MACHINE** | Consistent beats, raised guidance, compounding | CPRX |
| **TURNAROUND** | Business improving from distressed/losing state | COHR |
| **HYPE_MACHINE** | Momentum, retail enthusiasm, secular trend | MSTR |
| **LEGISLATIVE_TAILWIND** | Regulatory changes benefiting business | CPRX (OBBBA) |
| **PRODUCT_LAUNCH** | New product driving growth | |
| **SECULAR_GROWTH** | Long-term industry tailwind | CACI |
| **M&A_ACCELERATION** | Acquisition driving growth/strategic shift | CACI (ARKA) |
| **CYCLICAL_RECOVERY** | Business cycle upturn, temporarily depressed | ALGN |
| **FALLING_KNIFE_RECOVERY** | Rapid drop attempting recovery at support | |
| **GEOPOLITICALLY_STRATEGIC** | Sovereign asset, geopolitical importance | LYSDY |
| **POLICY_DRIVEN** | Government policy driving thesis | MP |
| **ENERGY_TRANSITION** | Nuclear/renewable energy theme | CEG |
| **PHYSICAL_INFRASTRUCTURE** | Hard assets powering AI/data centers | TER |
| **NICHE_IP_PLAY** | Small-cap with specialized intellectual property | AIP |
| **DEVELOPMENT_BINARY** | Pre-revenue, binary outcome on development | NXE |

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

## Scripts Reference

See [references/scripts.md](references/scripts.md) for complete documentation of all scripts including parameters, calculations, and data structures.

### Available Scripts

| Script | Purpose |
|--------|---------|
| get_portfolio.py | Display portfolio status and holdings (supports --portfolio, --list) |
| get_trade_log.py | View trade history with filters |
| update_portfolio_and_log.py | Execute BUY/SELL/TRIM trades (supports --portfolio) |
