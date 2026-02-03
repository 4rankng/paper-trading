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

# Analytics Generator - Quick Reference

Fetch price data and fundamental metrics, create data-driven analytics files for stock analysis.

**Key Principle:** Analytics = INSIGHTS, not RECOMMENDATIONS. Trading recommendations go in `trading-plans/` folder (use `/trade`).

---

## Quick Start

```bash
# Fetch prices
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA

# Get current price
python .claude/skills/analytics_generator/scripts/get_price.py --ticker NVDA

# Get fundamentals (JSON output)
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker NVDA

# List available price files
python .claude/skills/analytics_generator/scripts/list_prices.py
```

---

## When to Use

| Use | Don't Use |
|-----|-----------|
| Price data fetching/updating | Trading recommendations |
| Fundamental metrics | Watchlist screening |
| Creating analytics files | Portfolio operations |

**For trading recommendations:** Use `/trade` command
**For watchlist:** Use `watchlist_manager` skill
**For portfolio:** Use `portfolio_manager` skill

---

## Workflow Summary

### For New Stock Analysis

1. **Check news freshness** → `python .claude/skills/news_fetcher/scripts/list_news.py --ticker TICKER`
2. **Fetch price data** → `python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER`
3. **Generate technical** → `python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER`
4. **Aggregate signals** → `python .claude/skills/analytics_generator/scripts/aggregate_signals.py --ticker TICKER`
5. **Get fundamentals** → `python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TICKER`
6. **LLM creates analytics** → 3 markdown files in `analytics/{TICKER}/`

### Or Use /analyze Command

```bash
/analyze TICKER
```

Orchestrates all steps automatically: news check, price fetch, technical/fundamental data, signal dashboard, and LLM analytics creation.

---

## File Structure

| Location | Contents |
|----------|----------|
| `prices/{TICKER}.csv` | OHLCV data from yfinance (never edit manually) |
| `analytics/{TICKER}/` | 3 LLM-created markdown files |
| `news/{TICKER}/{YEAR}/{MONTH}/` | News articles with YAML frontmatter |

---

## Available Scripts

**Price Data:**
- `fetch_prices.py` - Fetch/update price data (batch: `NVDA AAPL MSFT`)
- `get_price.py` - Current price (batch supported)
- `get_prices.py` - Historical by period (1M, 3M, 6M, 1Y, 2Y)
- `list_prices.py` - List all price files

**Fundamentals:**
- `get_fundamental.py` - Fundamental metrics as JSON

**Technical:**
- `generate_technical.py` - Structured technical data (batch supported)
- `aggregate_signals.py` - Signal dashboard (appends to technical_analysis.md)

**Scoring (DUAL SYSTEM):**
- `quality_compound_scorer.py` - For proven businesses (15-30% CAGR)
- `multibagger_hunter_scorer.py` - For speculative stocks (5-10x potential)
- `llm_scorer.py` - Legacy general scorer

**See:** [Scripts Reference](references/scripts.md) for detailed documentation

---

## Scoring Systems

**IMPORTANT:** Use the correct scorer based on investment type.

| Stock Type | Use Scorer | Script |
|------------|------------|--------|
| Proven, profitable, compounding | Quality Compound Scorer | `quality_compound_scorer.py --ticker TICKER` |
| Speculative, early-stage, unprofitable | Multi-Bagger Hunter | `multibagger_hunter_scorer.py --ticker TICKER` |
| Mixed/unsure | Legacy LLM Scorer | `llm_scorer.py --ticker TICKER` |

**See:** [Scoring Systems Guide](references/scoring_systems_guide.md) for complete methodology

---

## Analytics Files (LLM-Created)

After running scripts, LLM creates 3 files in `analytics/{TICKER}/`:

1. **{TICKER}_technical_analysis.md** - Price action, indicators, trends + signal dashboard
2. **{TICKER}_fundamental_analysis.md** - Financials, business, risks
3. **{TICKER}_investment_thesis.md** - Thesis, catalysts, scenarios

**See:** [Analytics Files Reference](references/ANALYTICS_FILES.md) for complete structures

---

## Constraints

- **Never manually edit:** prices/*.csv, portfolio.json, watchlist.json, trade_log.csv
- **Max 1000 lines** per analytics markdown file
- **Analytics = INSIGHTS** - NO buy/sell/hold recommendations in analytics/
- **Trading recommendations** → `trading-plans/` folder (use `/trade`)

---

## Reference Material

| File | Purpose |
|------|---------|
| [Analytics Files Reference](references/ANALYTICS_FILES.md) | Complete markdown file structures |
| [Analysis Framework](references/analysis_framework.md) | 11-section framework definitions |
| [Scripts Reference](references/scripts.md) | All parameters and usage examples |
| [Scoring Systems Guide](references/scoring_systems_guide.md) | Quality Compound vs Multi-Bagger scoring |
