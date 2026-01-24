---
name: analytics-generator
description: Manage price data AND fundamental metrics, create data-driven analytics files (technical, fundamental, thesis). ALWAYS use for: "fetch price", "get price data", "historical prices", "current price", "update prices", "download prices", "list price files", "OHLCV data", "fundamental data", "get fundamentals", "company metrics". Use with /analyze command for comprehensive stock analysis. NOT for trading recommendations (use /trade command), NOT for screening (use watchlist_manager), NOT for portfolio operations (use portfolio_manager). Never manually edit price CSV files - use scripts for all price operations.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
  - WebSearch
  - Skill(ask)
---

# Analytics Generator - Price Data, Fundamentals & Analytics Management

Fetch price data and fundamental metrics, create data-driven analytics files for stock analysis. Analytics files provide INSIGHTS only, not trading recommendations.

## Quick Start

```bash
# Fetch prices (2 years initial, then incremental updates)
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA
python .claude/skills/analytics_generator/scripts/fetch_prices.py NVDA AAPL MSFT
python .claude/skills/analytics_generator/scripts/fetch_prices.py --tickers NVDA,AAPL,MSFT

# Get current price (single or multiple)
python .claude/skills/analytics_generator/scripts/get_price.py --ticker NVDA
python .claude/skills/analytics_generator/scripts/get_price.py NVDA AAPL MSFT

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
# Single ticker
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER

# Batch tickers (space-separated or comma-separated)
python .claude/skills/analytics_generator/scripts/fetch_prices.py TICKER1 TICKER2 TICKER3
python .claude/skills/analytics_generator/scripts/fetch_prices.py --tickers TICKER1,TICKER2,TICKER3
```

### Step 4: Generate Technical Data

```bash
# Single ticker
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER

# Multiple tickers
python .claude/skills/analytics_generator/scripts/generate_technical.py TICKER1 TICKER2 TICKER3
```

This script outputs structured technical data (not loaded into context).

### Step 5: Generate Signal Summary (NEW - Aggregates 40+ Technical Indicators)

```bash
# Single ticker - generates {TICKER}_signal_summary.md in analytics folder
python .claude/skills/analytics_generator/scripts/aggregate_signals.py --ticker TICKER

# Multiple tickers
python .claude/skills/analytics_generator/scripts/aggregate_signals.py --tickers TICKER1,TICKER2,TICKER3

# Compact format for quick overview
python .claude/skills/analytics_generator/scripts/aggregate_signals.py --ticker TICKER --format compact

# JSON format for programmatic access
python .claude/skills/analytics_generator/scripts/aggregate_signals.py --ticker TICKER --format json
```

**Signal Summary provides:**
- **Market Regime Detection**: Trending Up/Down, Ranging, or Volatile with confidence
- **Overall Technical Health Score**: 0-100 scale with classification (Strongly Bullish to Strongly Bearish)
- **Category Scores**: Momentum, Trend, Volatility, Volume, OB/OS with regime-based weighting
- **Signal Convergence**: % of signals aligned in one direction
- **Cross-Confirmation Analysis**: Bullish vs Bearish signal counts with divergence warnings
- **Key Signals**: Top 10 strongest signals by magnitude

**Output file:** `analytics/{TICKER}/{TICKER}_signal_summary.md`

This summary is created alongside traditional technical analysis and provides LLM agents with a unified scoring system for faster analysis.

### Step 6: Generate Fundamental Data

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

### Step 7: Data Gap Analysis (MANDATORY GATE)

**Before creating any analytics files, the LLM MUST actively identify data gaps:**

1. **Review all collected data:**
   - Technical data output from `generate_technical.py`
   - Fundamental data JSON from `get_fundamental.py` (check `data_quality` field)
   - News articles from `news/{TICKER}/`

2. **Identify gaps** across these dimensions:
   - **Fundamental gaps**: Missing metrics, incomplete financials, unclear business model
   - **Technical gaps**: Insufficient price history, unclear patterns, missing indicators
   - **Catalyst gaps**: No upcoming events, unclear timeline, missing earnings dates
   - **Sector Catalyst gaps** (CRITICAL for momentum stocks): No check for sector-wide drivers like:
     - Mega-IPOs in sector (e.g., SpaceX IPO affecting satellite stocks)
     - Peer group movement (are sector peers moving together?)
     - ETF flows and rebalancing
     - Regulatory/policy shifts affecting entire sector
     - M&A activity or consolidation rumors
   - **Sentiment gaps**: No recent news, unclear institutional flow, missing social sentiment
   - **Benchmark gaps**: No sector context, no relative strength comparison

3. **Use the `ask` skill for unresolved gaps:**
   ```bash
   /ask TICKER
   ```
   - The skill auto-filters self-answerable questions
   - Only asks questions requiring user input (private context, qualitative judgments)
   - Tracks history to avoid duplicate questions

4. **GATE CHECK - Do NOT proceed until:**
   - All critical data gaps are identified
   - `ask` skill is invoked for gaps requiring user input
   - User provides answers OR data is confirmed unavailable
   - Analysis can proceed with available information

**CRITICAL: Only produce final analytics after this gate is passed.** If new questions emerge during analysis, stop and use `/ask` before continuing.

### Step 8: Create Analytics Files (LLM)

Read the structured outputs from Steps 4-6 and create four markdown files:

1. `analytics/{TICKER}/{TICKER}_signal_summary.md` - from `aggregate_signals.py` (auto-generated, no LLM input needed)
2. `analytics/{TICKER}/{TICKER}_technical_analysis.md` - from `generate_technical.py`
3. `analytics/{TICKER}/{TICKER}_fundamental_analysis.md` - from `get_fundamental.py`
4. `analytics/{TICKER}/{TICKER}_investment_thesis.md` - synthesis of all data

**All three LLM-created files MUST incorporate insights from:**
- Signal summary (from `aggregate_signals.py`)
- Technical data (from `generate_technical.py`)
- Fundamental data (from `get_fundamental.py`)
- News articles (from `news/{TICKER}/`)
- User-provided answers from `ask` skill (if any)

For detailed section structures, see [Analytics Files Reference](references/ANALYTICS_FILES.md).

## Comprehensive Analysis with /analyze

The `/analyze [TICKER]` command orchestrates all skills:

1. **News freshness check** (MANDATORY)
2. **Price data fetching** via `fetch_prices.py`
3. **News fetching** via `news_fetcher` skill (if needed)
4. **Technical data generation** via `generate_technical.py`
5. **Signal summary generation** via `aggregate_signals.py` (NEW - aggregates 40+ indicators)
6. **Fundamental data generation** via `get_fundamental.py`
7. **Sector catalyst check** (NEW - for momentum stocks): Search for sector-wide drivers (IPOs, M&A, policy shifts)
8. **Data gap analysis** via `ask` skill (MANDATORY GATE)
9. **LLM analytics creation** (incorporates signal summary, technical, fundamental, news, sector catalysts, and user-provided answers)

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
- `fetch_prices.py` - Fetch/update price data from yfinance (2 years initial, then incremental). Supports batch tickers: `fetch_prices.py NVDA AAPL MSFT`
- `get_price.py` - Get current price with basic info. Supports batch: `get_price.py NVDA AAPL MSFT`
- `get_prices.py` - Get historical prices by period (1M, 3M, 6M, 1Y, 2Y)
- `list_prices.py` - List all available price files with metadata

**Fundamental Data:**
- `get_fundamental.py` - Get fundamental metrics as JSON (market cap, P/E, margins, growth, debt, ratios)

**Technical Analysis:**
- `generate_technical.py` - Generate structured technical data (execute, don't read). Supports batch: `generate_technical.py NVDA AAPL MSFT`
- `technical_indicators.py` - Utility module (imported by generate_technical.py)

**Signal Aggregation (NEW):**
- `aggregate_signals.py` - Aggregates 40+ technical indicators into unified scores. Supports batch: `aggregate_signals.py --tickers NVDA,AAPL,MSFT`
- `regime_classifier.py` - Detects market regime (trending/ranging/volatile)
- `signal_scorer.py` - Maps individual indicators to -1 to +1 scale
- `score_aggregator.py` - Combines signals into category and overall scores
- `signal_weights.yaml` - Configuration for regime-based weights

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
