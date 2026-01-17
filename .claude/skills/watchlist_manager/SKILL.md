---
name: watchlist-manager
description: Manage watchlist.json for tracking potential investments. ALWAYS use for watchlist CRUD operations: add/update/remove stocks, search, filter, get summary. **MANDATORY PRE-WORKFLOW**: Before ANY add/update with strategy classification, MUST use analytics_generator skill to create analytics/[TICKER]/ files (technical, fundamental, thesis), then READ those files to determine strategy/hold/fit. Never directly edit watchlist.json.
---

# Watchlist Manager

Lean JSON-based watchlist for tracking potential investments.

## CRITICAL: Pre-Workflow Before Add/Update

**Before adding or updating a stock with strategy classification, you MUST:**

1. **Use `analytics_generator` skill** to ensure analytics files exist:
   ```bash
   # Fetch price data
   python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER

   # Generate technical data
   python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER

   # Get fundamental metrics
   python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TICKER
   ```

2. **Read the analytics files** to determine strategy classification:
   - `analytics/{TICKER}/{TICKER}_technical_analysis.md`
   - `analytics/{TICKER}/{TICKER}_fundamental_analysis.md`
   - `analytics/{TICKER}/{TICKER}_investment_thesis.md`

3. **Only then** determine `strategy`, `hold`, and `fit` from the analytics

**If analytics files don't exist, create them using the analytics_generator skill first.**

## Quick Start

```bash
# Add a stock (after analyzing technical data)
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --add --ticker NVDA --name "NVIDIA" --sector "Technology" \
  --strategy trend_rider --hold "2w-3m" --fit 85 \
  --add-action WATCH --price 150

# Search by ticker
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py --ticker NVDA

# Filter by strategy
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --filter-strategy trend_rider --format compact

# Get summary
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py --summary
```

## Schema

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA",
  "sector": "Technology",
  "strategy": "trend_rider",
  "hold": "2w-3m",
  "fit": 85,
  "action": "WATCH",
  "price": 150.00,
  "exit": 200.00,
  "stop": 120.00,
  "rr": 2.50,
  "updated_at": "2026-01-18"
}
```

**Unclassified stock (no strategy assigned):**
```json
{
  "ticker": "HUBS",
  "name": "HubSpot",
  "sector": "Technology",
  "strategy": null,
  "hold": null,
  "action": "WATCH",
  "price": 311.88,
  "updated_at": "2026-01-18"
}
```

| Field | Values | Rules |
|-------|--------|-------|
| `strategy` | From [strategies.md](references/strategies.md) or `null` | Only set if fit >= 60; otherwise `null` |
| `hold` | `1-10d`, `2w-3m`, `3-6m`, `1y+` or `null` | Only set if strategy is defined |
| `fit` | 0-100 | Only included if strategy is defined |
| `action` | `BUY`, `SELL`, `WATCH`, `AVOID` | Always required |
| `price` | Current price | Optional |
| `exit`, `stop`, `rr` | Trading levels | Only included if strategy is defined |
| `updated_at` | YYYY-MM-DD | Auto-set on add/update |

## LLM Workflow for Adding Stocks

Follow the **CRITICAL Pre-Workflow** above first. Then:

1. **Read analytics files**
   ```bash
   # Read these files using Read tool
   analytics/{TICKER}/{TICKER}_technical_analysis.md
   analytics/{TICKER}/{TICKER}_fundamental_analysis.md
   analytics/{TICKER}/{TICKER}_investment_thesis.md
   ```

2. **Determine strategy/hold/fit from analytics**
   - Use [strategies.md](references/strategies.md) for complete criteria
   - Calculate fit score (0-100) from technicals + fundamentals
   - Only assign strategy if **fit >= 60**
   - If fit < 60, set `strategy: null`, `hold: null`

3. **If classified (fit >= 60), calculate trading levels**
   - Entry: Current price or support level
   - Stop: Below support or 20/50 EMA
   - Exit: At resistance or 2-3x risk
   - Verify R:R ≥ 2.0

4. **Add to watchlist**
   ```bash
   # Classified example (fit >= 60)
   python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
     --add --ticker TICKER --name "Company" --sector "Sector" \
     --strategy trend_rider --hold "2w-3m" --fit 75 \
     --add-action WATCH --price 150 --exit 180 --stop 135

   # Unclassified example (fit < 60)
   python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
     --add --ticker TICKER --name "Company" --sector "Sector" \
     --add-action WATCH --price 150
   ```

## CLI Reference

| Mode | Arguments | Description |
|------|-----------|-------------|
| `--add` | `--ticker`, `--name`, `--sector` (required) | Add new stock |
| | `--strategy`, `--hold`, `--fit` | Classification from analytics |
| | `--add-action` | BUY/SELL/WATCH/AVOID |
| | `--price`, `--exit`, `--stop` | Price levels |
| `--update` | `--ticker` (required) | Update existing stock |
| | Same as add for fields to update | |
| `--remove` | `--ticker` (required) | Remove stock |
| Search | `--ticker`, `--tickers`, `--sector`, `--action` | Filter results |
| | `--filter-strategy`, `--holding-period`, `--min-fit` | |
| | `--min-price`, `--max-price`, `--min-rr` | |
| | `--sort`, `--top` | Sort and limit |
| `--summary` | | Get watchlist statistics |
| `--format` | `json`, `compact`, `human` | Output style |

## Strategy List

For detailed criteria, see [strategies.md](references/strategies.md).

| Period | Strategies |
|--------|------------|
| 1-10d | `gap_and_go`, `intraday_reversal`, `high_relative_vol` |
| 2w-3m | `trend_rider`, `mean_reversion`, `volatility_squeeze` |
| 3-6m | `canslim`, `golden_cross` |
| 1y+ | `quality_discount`, `dividend_aristocrat` |

## Rules

1. **MANDATORY: Use analytics_generator skill FIRST** - Create analytics files before any add/update with strategy
2. **Only classify if fit >= 60** - Otherwise set `strategy: null`, `hold: null`
3. **Never use "unclassified" or "unknown" strings** - Use `null` instead
4. **Trading fields (exit, stop, rr, fit) ONLY when strategy defined** - Auto-removed if `strategy: null`
5. **Always read analytics files before determining strategy** - Don't guess from ticker alone
6. **Use exact strategy names** - Must match values in strategies.md
7. **Classified stocks MUST have trading levels** - Entry (price), Exit, Stop with R:R ≥ 2.0
8. **updated_at auto-set on every add/update** - Script handles this automatically

## Trading Level Guidelines

When classifying a stock, calculate levels from technical analysis:

| Level | How to Determine |
|-------|------------------|
| **Entry** | Current price or pullback to support |
| **Stop** | Below support (S1) or below 20/50 EMA for trend trades |
| **Exit** | At resistance (R1/R2) or 2-3x risk for trend trades |
| **Min R:R** | ≥ 2.0 required; avoid setups with lower ratios |
