# Market Update Workflows

This document describes the detailed workflows, error handling, and data freshness strategies for the market update command.

## Step-by-Step Workflow

### Step 1: Get Holdings Summary

**Script:** `get_holdings_summary.py`

**Process:**
1. Load portfolio from `filedb/portfolios.json` using `DataAccess.get_portfolio()`
2. Extract holdings list with ticker, shares, avg_cost, current_price, status
3. Calculate market_value = shares × current_price
4. Calculate gain_loss = market_value - (shares × avg_cost)
5. Calculate gain_loss_pct = (gain_loss / cost_basis) × 100

**Error Handling:**
- Portfolio not found → Raise ValueError with available portfolios
- No holdings → Return empty holdings list with warning
- Missing current_price → Use 0.0 and calculate with warning

**Output:**
```json
{
  "portfolio_name": "CORE",
  "description": "Main autonomous driving positions",
  "cash": 22.18,
  "holdings": [
    {
      "ticker": "LAES",
      "shares": 18000,
      "avg_cost": 6.4,
      "current_price": 3.52,
      "market_value": 63360.0,
      "gain_loss": -51840.0,
      "gain_loss_pct": -45.0,
      "status": "active"
    }
  ],
  "summary": {
    "holdings_value": 103610.0,
    "total_cost_basis": 176240.0,
    "total_gain_loss": -72630.0,
    "total_gain_loss_pct": -41.22,
    "holdings_count": 3
  }
}
```

### Step 2: Fetch Current Prices

**Script:** `fetch_current_prices.py`

**Process:**
1. For each ticker, try CSV file first (`prices/{TICKER}.csv`)
2. Check CSV freshness (last row age <24h)
3. If CSV is stale or missing, fetch from yfinance
4. Calculate change from previous close

**Error Handling:**
- Invalid ticker → Skip with warning
- yfinance timeout → Fallback to CSV with staleness warning
- No price data → Mark as "N/A" with warning

**Output:**
```json
{
  "LAES": {
    "price": 3.52,
    "change": -0.09,
    "change_pct": -2.5,
    "date": "2026-02-07",
    "source": "yfinance",
    "age_hours": 0.1
  }
}
```

### Step 3: Aggregate Latest News

**Script:** `aggregate_news.py`

**Process:**
1. For each ticker, list existing news files from `news/{TICKER}/{YYYY}/{MM}/`
2. Check freshness of latest file (<24h old)
3. If fresh, extract headlines from YAML frontmatter
4. If stale/missing, signal need for WebSearch (empty list)

**Error Handling:**
- No news directory → Return empty list
- News files stale → Return empty list (signal for WebSearch)
- Invalid file format → Skip with warning

**Output:**
```json
{
  "news": {
    "LAES": [
      {
        "headline": "LAES announces strategic partnership",
        "source": "Company PR",
        "date": "2026-02-07 12:00",
        "age_hours": 2.5
      }
    ]
  },
  "freshness": {
    "LAES": true,
    "WRD": false
  }
}
```

### Step 4: Check Macro Context

**Script:** `check_macro.py`

**Process:**
1. Read latest macro thesis from `macro/theses/macro_thesis_YYYY_MM.md`
2. Extract stance (RISK-ON/RISK-OFF/NEUTRAL) and risk_level (HIGH/MEDIUM/LOW)
3. Extract executive summary (first 200 chars)
4. Check thesis age (days since last update)

**Error Handling:**
- No macro thesis → Return "No macro analysis available"
- Thesis stale (>7 days) → Add warning message
- Invalid file format → Return "UNKNOWN" stance

**Output:**
```json
{
  "fear_greed": {
    "value": null,
    "label": null,
    "available": false
  },
  "macro_thesis": {
    "stance": "RISK-ON",
    "risk_level": "MEDIUM",
    "summary": "Moderate growth with policy uncertainty.",
    "date": "2026-02",
    "available": true,
    "age_days": 5.0
  },
  "warnings": [
    "Fear & Greed Index to be fetched by LLM agent"
  ]
}
```

**Note:** CNN Fear & Greed Index is fetched by the LLM agent using webReader tool during skill invocation.

### Step 5: LLM Thesis Reassessment

**Script:** `reassess_thesis.py`

**Process:**
1. For each ticker, read existing thesis from `analytics/{TICKER}/{TICKER}_investment_thesis.md`
2. Gather latest news (max 5 headlines with age)
3. Get current price and daily change %
4. Generate LLM prompt with all inputs
5. Prompt LLM to assess status (VALID/DEAD/WARNING/UNKNOWN)

**LLM Prompt Structure:**
```
You are assessing the validity of an investment thesis for {TICKER} based on fresh data.

EXISTING THESIS (if available):
{thesis_summary}

LATEST NEWS (last 24h):
• News headline 1 (2h ago)
• News headline 2 (6h ago)

CURRENT PRICE ACTION:
Price: $3.52 (Daily Change: -2.5%)

ASSESSMENT TASK:
Based on the fresh news and price action, determine if the investment thesis remains VALID or has become DEAD.

OUTPUT FORMAT (JSON only, no markdown):
{
  "status": "VALID" | "DEAD" | "WARNING" | "UNKNOWN",
  "rationale": "2-3 sentence explanation",
  "key_changes": ["key change 1", "key change 2"],
  "confidence": "HIGH" | "MEDIUM" | "LOW"
}

Apply Inertia Principle: Existing positions are VALID unless proven DEAD.
```

**Error Handling:**
- No existing thesis → Set status to "UNKNOWN" with note
- No news available → Use price action only, confidence="LOW"
- LLM parsing error → Return status="UNKNOWN" with error message
- LLM timeout → Return status="UNKNOWN", confidence="LOW"

**Output:**
```json
{
  "LAES": {
    "ticker": "LAES",
    "status": "VALID",
    "rationale": "Strong earnings beat and new partnership validate growth thesis. Price drop is market overreaction.",
    "key_changes": [
      "Q4 earnings beat expectations",
      "Strategic partnership announced"
    ],
    "confidence": "HIGH",
    "prompt": "...",
    "thesis_exists": true,
    "news_count": 5,
    "price_available": true
  }
}
```

**CRITICAL:** This script does NOT update thesis files automatically. It only generates the prompt and reports the reassessment status. The LLM agent uses the prompt to generate the assessment.

### Step 6: Generate Terminal Output

**Script:** `market_update.py`

**Process:**
1. Combine all data from previous steps
2. Format with viz:table for holdings
3. Format with viz:chart for P/L comparison (optional)
4. Include macro summary at top
5. Add latest news and thesis reassessment
6. Include data freshness warnings at bottom

**Output Sections:**
1. Header (portfolio name, timestamp)
2. Market Context (Fear & Greed, Macro Stance, Summary)
3. Holdings Summary (viz:table)
4. Portfolio Totals (Total Value, Cash, Total P/L)
5. Latest News (grouped by ticker with thesis status)
6. Thesis Reassessment (LLM Analysis table)
7. Data Freshness (status indicators)

## Error Handling Matrix

| Error Scenario | Detection | Response |
|----------------|-----------|----------|
| No holdings in portfolio | `len(holdings) == 0` | "No holdings found in CORE portfolio." |
| Portfolio not found | `ValueError` from DataAccess | "Portfolio 'XXX' not found. Available: CORE, LLM_HELP" |
| Price CSV missing/stale | `not csv_path.exists()` or `>24h` | Fetch from yfinance with warning |
| yfinance timeout | `requests.Timeout` | Fallback to CSV with staleness warning |
| No news files | `len(news_files) == 0` | Use WebSearch for fresh headlines |
| News files stale | `age_hours > 24` | Fetch fresh via WebSearch |
| WebSearch failed | `WebSearch` error | Return empty news list with warning |
| Analytics files missing | `not thesis_path.exists()` | Set status="UNKNOWN" in reassessment |
| Fear & Greed unreachable | `webReader` error | Show "N/A" for Fear & Greed |
| No macro thesis | `len(theses) == 0` | Warning: "No macro analysis available" |
| Macro thesis stale | `age_days > 7` | Warning: "Macro thesis is X days old" |
| LLM reassessment fails | LLM error | Set status="UNKNOWN", confidence="LOW" |

## Data Freshness Strategy

| Data Type | Fresh | Stale | Action When Stale |
|-----------|-------|-------|-------------------|
| Prices | <1h old | >24h old | Fetch from yfinance |
| News | <24h old | >24h old | WebSearch for fresh headlines |
| Thesis | N/A | N/A | Always reassess with LLM using fresh news |
| Macro Thesis | <7 days old | >7 days old | Warning only |
| Fear & Greed | <1h old | >1h old | Show staleness warning |

**Key Principles:**
1. **Data Freshness First:** Always check file timestamps before using cached data
2. **Graceful Degradation:** Continue with partial data if some components fail
3. **Error Resilience:** Never crash on missing data; show warnings instead
4. **User Control:** Allow `--force-refresh` to bypass cache and fetch all fresh data

## LLM Integration Points

### CNN Fear & Greed Index
- **When:** During skill invocation (Step 4)
- **Tool:** `mcp__web-reader__webReader`
- **URL:** https://edition.cnn.com/markets/fear-and-greed
- **Parsing:** Extract numeric value and label (Extreme Fear → Neutral → Extreme Greed)

### Fresh News via WebSearch
- **When:** When news files are stale or missing (Step 3)
- **Tool:** `WebSearch` or `mcp__web-search-prime__webSearchPrime`
- **Query:** "{TICKER} stock news last 24 hours"
- **Limit:** Top 5 headlines per ticker
- **Output:** Headline, source, URL, age

### LLM Thesis Reassessment
- **When:** After news and prices are gathered (Step 5)
- **Input:** Existing thesis (if any), latest news, price action
- **Prompt:** Generated by `reassess_thesis.py`
- **Output:** JSON with status, rationale, key_changes, confidence
- **Storage:** NOT stored to files; only displayed in output

## Multi-Portfolio Support

### Default Portfolio
- Uses `metadata.default_portfolio` from `portfolios.json`
- Typically "CORE" unless changed

### Specified Portfolio
- Use `--portfolio` flag to target specific portfolio
- Example: `/market-update --portfolio LLM_HELP`

### Available Portfolios
- List all portfolios: `python .claude/skills/portfolio_manager/scripts/get_portfolio.py --list`
- Error message shows available portfolios if specified name not found

## Command Examples

### Basic Usage
```bash
# Market update for default portfolio
/market-update

# Market update for specific portfolio
/market-update --portfolio CORE

# Force refresh all data (ignore cache)
/market-update --force-refresh
```

### Script Testing
```bash
# Test holdings summary
python .claude/skills/market_update/scripts/get_holdings_summary.py --portfolio CORE

# Test price fetching
python .claude/skills/market_update/scripts/fetch_current_prices.py --tickers LAES,WRD,PONY

# Test news aggregation
python .claude/skills/market_update/scripts/aggregate_news.py --tickers LAES --limit 5

# Test macro context
python .claude/skills/market_update/scripts/check_macro.py

# Test thesis reassessment (prompt only)
python .claude/skills/market_update/scripts/reassess_thesis.py --ticker LAES --format prompt

# Test full workflow (JSON output)
python .claude/skills/market_update/scripts/market_update.py --portfolio CORE --format json
```
