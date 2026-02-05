---
name: watchlist-manager
description: Manage watchlist.json for tracking potential investments. ALWAYS use for watchlist CRUD operations: add/update/remove stocks, search, filter, get summary. **MANDATORY PRE-WORKFLOW**: Before ANY add/update with strategy classification, MUST use analytics_generator skill to create analytics/[TICKER]/ files (technical, fundamental, thesis), then READ those files to determine strategy/hold/fit. Never directly edit watchlist.json.
allowed-tools:
  - Read
  - Bash(python:*)
---

# Watchlist Manager

Lean JSON-based watchlist for tracking potential investments.

## CRITICAL: Visualization Output Format

**NEVER use markdown tables for data output.** Use the visualization format specified in [../references/visualization-guide.md](../references/visualization-guide.md).

### Quick Reference for Watchlist Display

**For watchlist summary - USE viz:table:**
```
![viz:table]({"headers":["Ticker","Strategy","Fit","Status"],"rows":[["NVDA","MEAN_REVERSION",85,"WATCH"],["AAPL","EARNINGS_MACHINE",92,"BUY"]]})
```

**For strategy distribution - USE viz:pie:**
```
![viz:pie]({"data":[{"label":"EARNINGS_MACHINE","value":5},{"label":"MEAN_REVERSION","value":3},{"label":"HYPE_MACHINE","value":2}]})
```

### FORBIDDEN (Do NOT use):
❌ Markdown tables: `| Ticker | Strategy |`
❌ ASCII art: `+-------+----------+`

## v3.0 Minimal Schema

**CRITICAL:** `watchlist.json` stores ONLY minimal tracking data. All analysis data (name, sector, notes, scores, etc.) MUST be in `analytics/[TICKER]/` folder.

## CRITICAL: Pre-Workflow Before Add/Update

**Before adding or updating a stock with strategy classification, you MUST:**

1. **Use `analytics_generator` skill** to ensure analytics files exist:
   ```bash
   # Fetch price data (single or batch)
   python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER
   python .claude/skills/analytics_generator/scripts/fetch_prices.py TICKER1 TICKER2 TICKER3

   # Generate technical data
   python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER

   # Get fundamental metrics
   python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TICKER
   ```

2. **Follow the 3-step Data-First Decision Making checklist:**
   **[Data-First Decision Making](references/data-first-decision-making.md)**

3. **Only then** determine `strategy`, `hold`, and `fit` from the analytics + fresh data

**If analytics files don't exist or are >24h old, create them using the analytics_generator skill first.**

## Data Gap Detection (Before Add/Update)

**Before adding or updating with strategy classification, check for data gaps using the `ask` skill.**

See [Data Gap Detection Workflow](references/data-gap-detection.md) for the complete process.

**Priority gaps for watchlist_manager:** Strategy unclear, fit score impossible, missing analytics.

**If strategy is unavailable**, set `strategy: null` and `hold: null` (unclassified entry).

---

## Quick Start

```bash
# Add a stock (after analyzing technical data)
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --add --ticker NVDA --investment-type compounder \
  --strategy trend_rider --hold "2w-3m" --fit 85 \
  --action WATCH --price 150

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
  "investment_type": "compounder",
  "strategy": "trend_rider",
  "hold": "2w-3m",
  "fit": 85,
  "buy_score": 75,
  "action": "WATCH",
  "price": 150.00,
  "exit": 200.00,
  "stop": 120.00,
  "rr": 2.50,
  "updated_at": "2026-01-18"
}
```

**Moonshot stock (unclassified - no strategy):**
```json
{
  "ticker": "LAES",
  "investment_type": "moonshot",
  "strategy": null,
  "hold": null,
  "action": "WATCH",
  "price": 4.50,
  "buy_score": 100,
  "updated_at": "2026-01-29"
}
```

**Allowed fields:** `ticker`, `investment_type`, `strategy`, `hold`, `fit`, `buy_score`, `action`, `price`, `exit`, `stop`, `rr`, `updated_at`

**Analysis data (removed - use analytics/[TICKER]/):** `name`, `sector`, `notes`, `quality_score`, `dbs_*`, `fair_*`, `gatekeepers_*`, `multibagger_*`, etc.

| Field | Values | Rules |
|-------|--------|-------|
| `investment_type` | **`compounder`** or **`moonshot`** | **REQUIRED** - determines scoring system |
| `strategy` | From [strategies.md](references/strategies.md) or `null` | Only set if fit >= 60; otherwise `null` |
| `hold` | `1-10d`, `2w-3m`, `3-6m`, `1y+` or `null` | Only set if strategy is defined |
| `fit` | 0-100 | **Strategy fit** - how well stock matches trading strategy criteria |
| `buy_score` | 0-100 | **Buy attractiveness** - how attractive to buy NOW (independent of strategy) |
| `action` | `BUY`, `SELL`, `WATCH`, `AVOID` | Always required |
| `price` | Current price | Optional |
| `exit`, `stop`, `rr` | Trading levels | Only included if strategy is defined |
| `notes` | Brief key insight | **Max 10 words. No fluff.** |
| `updated_at` | YYYY-MM-DD | Auto-set on add/update |

---

## Investment Types (CRITICAL)

### COMPOUNDER
- **Definition:** Proven, profitable businesses targeting 15-30% CAGR
- **Scoring System:** Quality Compound Scorer
- **Max Position Size:** 10-20% of portfolio
- **Time Horizon:** 5-10 years
- **Characteristics:** Positive earnings, strong ROE, wide moat, reasonable valuation
- **Examples:** MSFT, AAPL, GOOGL, TSM, JPM

### MOONSHOT
- **Definition:** Speculative, high-growth stocks targeting 5-10x potential
- **Scoring System:** Multi-Bagger Hunter
- **Max Position Size:** 2-5% of portfolio (binary risk)
- **Time Horizon:** 3-7 years
- **Characteristics:** Unprofitable acceptable, rich valuation OK, TAM $100B+, visionary founder
- **Examples:** LAES, RZLV, PONY, WRD, early-stage AI/biotech

---

## Which Scorer to Use?

| Investment Type | Use Scorer | Script |
|-----------------|------------|--------|
| `compounder` | Quality Compound Scorer | `quality_compound_scorer.py --ticker TICKER` |
| `moonshot` | Multi-Bagger Hunter | `multibagger_hunter_scorer.py --ticker TICKER` |

### Score Distinction

- **`fit`** (Strategy Fit): How well the stock matches a specific trading strategy's criteria
  - Determined from technical + fundamental analysis
  - Used to decide IF a stock belongs to a strategy
  - Only set when `strategy` is defined (fit < 60 → unclassified)

- **`buy_score`** (Buy Attractiveness): How attractive the stock is to buy right now
  - Independent of strategy classification
  - Based on: valuation, technical setup, catalysts, risk/reward
  - Set for ALL stocks (classified or not)
  - Used for ranking: `--rank` command sorts by buy_score

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

1. **MANDATORY: Set investment_type** - Every stock must be classified as `compounder` or `moonshot`
2. **MANDATORY: Use analytics_generator skill FIRST** - Create analytics files before any add/update with strategy
3. **NEVER add non-stock tickers (CASH, MONEY, MMKT)** - Cash/money market positions belong in `portfolios.json` (shared cash pool), NOT `watchlist.json`
4. **Only classify if fit >= 60** - Otherwise set `strategy: null`, `hold: null`
5. **Never use "unclassified" or "unknown" strings** - Use `null` instead
6. **Trading fields (exit, stop, rr, fit) ONLY when strategy defined** - Auto-removed if `strategy: null`
7. **Always read analytics files before determining strategy** - Don't guess from ticker alone
8. **Use exact strategy names** - Must match values in strategies.md
9. **Classified stocks MUST have trading levels** - Entry (price), Exit, Stop with R:R ≥ 2.0
10. **updated_at auto-set on every add/update** - Script handles this automatically
11. **Notes must be concise (max 10 words)** - Include only key metrics, catalyst, or entry guidance

---

## Classification Workflow

When adding a new stock:

1. **Determine investment_type first** (compounder vs moonshot)
   - Read the thesis and fundamentals
   - Set `investment_type: "compounder"` or `investment_type: "moonshot"`

2. **Run the correct scorer**
   ```bash
   # For compounders
   python .claude/skills/analytics_generator/scripts/quality_compound_scorer.py --ticker TICKER

   # For moonshots
   python .claude/skills/analytics_generator/scripts/multibagger_hunter_scorer.py --ticker TICKER
   ```

3. **Then set strategy/hold/fit** based on the scoring results

## Trading Level Guidelines

When classifying a stock, calculate levels from technical analysis:

| Level | How to Determine |
|-------|------------------|
| **Entry** | Current price or pullback to support |
| **Stop** | Below support (S1) or below 20/50 EMA for trend trades |
| **Exit** | At resistance (R1/R2) or 2-3x risk for trend trades |
| **Min R:R** | ≥ 2.0 required; avoid setups with lower ratios |
