---
name: analytics-generator
description: Manage price data AND fundamental metrics, create data-driven analytics files (technical, fundamental, thesis). ALWAYS use for: "fetch price", "get price data", "historical prices", "current price", "update prices", "download prices", "list price files", "OHLCV data", "fundamental data", "get fundamentals", "company metrics". Use with /analyze command for comprehensive stock analysis. NOT for trading recommendations (use /trade command), NOT for screening (use watchlist_manager), NOT for portfolio operations (use portfolio_manager). Never manually edit price CSV files - use scripts for all price operations.
---

# Analytics Generator - Price Data, Fundamentals & Analytics Management

Fetch price data and fundamental metrics, create data-driven analytics files for stock analysis. Analytics files provide INSIGHTS only, not trading recommendations.

## Quick Start

```bash
# Fetch prices (2 years initial, then incremental updates)
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA

# Get current price
python .claude/skills/analytics_generator/scripts/get_price.py --ticker NVDA

# Get fundamental metrics (JSON output)
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker NVDA

# Get historical prices (1M, 3M, 6M, 1Y, 2Y)
python .claude/skills/analytics_generator/scripts/get_prices.py --ticker TCOM --period 6M

# List available price files
python .claude/skills/analytics_generator/scripts/list_prices.py
```

## When to Use

**Use for:**
- Price data fetching and updates
- Historical price queries
- Current price checks
- Fundamental metrics (market cap, P/E ratios, margins, growth rates, balance sheet)
- Creating data-driven analytics files (technical, fundamental, thesis)

**NOT for:**
- Trading recommendations (use `/trade` command)
- Watchlist screening (use `watchlist_manager` skill)
- Portfolio operations (use `portfolio_manager` skill)

## Mandatory Workflow

**CRITICAL: Analytics generation requires BOTH price data AND current news.**

### Step 1: Check News Freshness (MANDATORY)

```bash
# List existing news articles
python .claude/skills/news_fetcher/scripts/list_news.py --ticker TICKER
```

**Review output:**
- **No articles** → News directory missing/empty → proceed to Step 2
- **Articles exist** → Check most recent `published_date`:
  - Older than 3 days → stale → proceed to Step 2
  - Within 3 days → fresh → skip to Step 3

### Step 2: Web Search (if news is stale/missing)

If news is stale or missing, perform web search:
```
Search for: "{TICKER} stock news latest"
```

Identify significant articles (earnings, guidance, product launches, management changes, regulatory news).

**Add important articles via news_fetcher:**
```bash
python .claude/skills/news_fetcher/scripts/add_news.py \
  --ticker TICKER --title "Title" --source "Source" \
  --url "https://..." --content "Content..."
```

### Step 3: Fetch Price Data

```bash
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER
```

### Step 4: Generate Technical Data

```bash
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER
```

This script outputs structured technical data (not loaded into context).

### Step 5: Generate Fundamental Data

```bash
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TICKER
```

This script outputs structured fundamental data as JSON (market cap, P/E ratios, margins, growth, balance sheet).

**CRITICAL: Always check `data_quality` field before analysis:**

```json
{
  "ticker": "NVDA",
  "data_quality": {
    "completeness_pct": 90,
    "critical_fields_present": true,
    "warnings": [],
    "missing_critical": [],
    "missing_optional": ["fifty_two_week_change"]
  },
  "market_cap": 4534141714432,
  ...
}
```

**Validation Rules:**
- `critical_fields_present: false` → DO NOT proceed with analysis - use web search fallback
- `completeness_pct < 50` → Data unreliable - warn user and consider web search fallback
- Exit code 1 = critical fields missing (check stderr for warnings)

**Critical Fields:** market_cap, current_price, sector, industry

**Fallback to Web Search (when validation fails):**

If `critical_fields_present: false` or `completeness_pct < 50`:

1. Search for: "{TICKER} fundamental analysis market cap PE ratio"
2. Search for: "{TICKER} sector industry financial metrics"
3. Search for: "{TICKER} key statistics revenue margins debt"

Extract available fundamentals from web results and note data limitations in analysis.

### Step 6: Create Analytics Files (LLM)

Read the structured outputs from Steps 4-5 and create three markdown files:

1. `analytics/{TICKER}/{TICKER}_technical_analysis.md` - from `generate_technical.py`
2. `analytics/{TICKER}/{TICKER}_fundamental_analysis.md` - from `get_fundamental.py`
3. `analytics/{TICKER}/{TICKER}_investment_thesis.md` - synthesis of all data

**All three files MUST incorporate insights from:**
- Technical data (from `generate_technical.py`)
- Fundamental data (from `get_fundamental.py`)
- News articles (from `news/{TICKER}/`)

For detailed section structures, see [Analytics Files Reference](references/ANALYTICS_FILES.md).

## Comprehensive Analysis with /analyze

The `/analyze [TICKER]` command orchestrates all skills:

1. **News freshness check** (MANDATORY)
2. **Price data fetching** via `fetch_prices.py`
3. **News fetching** via `news_fetcher` skill (if needed)
4. **Technical data generation** via `generate_technical.py`
5. **Fundamental data generation** via `get_fundamental.py`
6. **LLM analytics creation** (incorporates price, fundamental, and news data)

## File Structure

**Price Data:** `prices/{TICKER}.csv`
- CSV: Date, Open, High, Low, Close, Volume, Dividends, Stock Splits
- Managed by yfinance API
- **Never edit manually** - use scripts only

**Analytics:** `analytics/{TICKER}/`
- Data-driven insights only (NO trading recommendations)
- LLM-created markdown files
- Max 1000 lines per file (compress if exceeded)

**News:** `news/{TICKER}/{YEAR}/{MONTH}/{SLUG}.md`
- YAML frontmatter with metadata
- Content for fundamental and thesis analysis

## Available Scripts

**Price Data Operations:**
- `fetch_prices.py` - Fetch/update price data from yfinance (2 years initial, then incremental)
- `get_price.py` - Get current price with basic info
- `get_prices.py` - Get historical prices by period (1M, 3M, 6M, 1Y, 2Y)
- `list_prices.py` - List all available price files with metadata

**Fundamental Data:**
- `get_fundamental.py` - Get fundamental metrics as JSON (market cap, P/E, margins, growth, debt, ratios)

**Technical Analysis:**
- `generate_technical.py` - Generate structured technical data (execute, don't read)
- `technical_indicators.py` - Utility module (imported by generate_technical.py)

**Scripts are EXECUTED, not READ.** Run them via Bash tool and consume output only.

## Constraints

**File Management:**
- **Never manually edit:** prices/*.csv, portfolio.json, watchlist.json, trade_log.csv
- **Max 1000 lines** per analytics markdown file
- Scripts provide data, LLM creates markdown files

**Analytics Purpose:**
- Analytics = INSIGHTS, not RECOMMENDATIONS
- NO buy/sell/hold in analytics/
- NO position sizing in analytics/
- Trading recommendations → `trading-plans/` folder (use `/trade`)
- Signals → `signals/` folder (use `signal-formatter`)

**Investment Logic:**
- Existing holdings → Inertia Principle (VALID unless proven DEAD)
- New analysis → Benchmark Gate (must outperform S&P 500)
- Position sizing → Max 0.25% for new buys failing Benchmark Gate

**Probability Calibration:**
- Scenarios use ranges (X-Y%), not fixed percentages
- Calibrate by: phenomenon type, confidence, data quality, market conditions

## Reference Material

- **[Analytics Files Reference](references/ANALYTICS_FILES.md)** - Complete markdown file structures (technical, fundamental, thesis)
- **[Analysis Framework](references/analysis_framework.md)** - 11-section framework definitions
- **[Scripts Reference](references/scripts.md)** - All parameters and usage examples
