# Analytics Generator Scripts Reference

Documentation for price data management scripts.

## Available Scripts

### fetch_prices.py

Fetch and update price data from yfinance API.

**Usage:**
```bash
# Fetch 2 years of historical data (initial fetch)
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA

# Incremental update (subsequent runs)
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA
```

**Output:**
- Creates/updates `prices/{TICKER}.csv`
- Initial fetch: 2 years of daily OHLCV data
- Subsequent fetches: Incremental updates (only new data)

**Data Format:**
- CSV columns: Date, Open, High, Low, Close, Volume, Dividends, Stock Splits
- Date range: 2 years from first fetch
- Update frequency: Can be run daily for latest data

---

### get_price.py

Get current price for a ticker.

**Usage:**
```bash
python .claude/skills/analytics_generator/scripts/get_price.py --ticker NVDA
```

**Output:**
- Current price and basic info
- Latest trading date
- Price change from previous close

---

### get_prices.py

Get historical prices for a specific period.

**Usage:**
```bash
# Get last 6 months of prices
python .claude/skills/analytics_generator/scripts/get_prices.py --ticker TCOM --period 6M

# Available periods: 1M, 3M, 6M, 1Y, 2Y
python .claude/skills/analytics_generator/scripts/get_prices.py --ticker AAPL --period 1Y
```

**Periods:**
- `1M` - 1 month
- `3M` - 3 months
- `6M` - 6 months
- `1Y` - 1 year
- `2Y` - 2 years

---

### list_prices.py

List all available price CSV files.

**Usage:**
```bash
python .claude/skills/analytics_generator/scripts/list_prices.py
```

**Output:**
- List of all tickers with price data
- File paths
- Date ranges
- Data point counts

---

### get_fundamental.py

Get fundamental metrics for a ticker from yfinance.

**Usage:**
```bash
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker NVDA
```

**Output:** JSON with fundamental metrics:
- Market Data: market_cap, shares_outstanding, current_price, 52-week range/change
- Valuation: trailing_pe, forward_pe, price_to_sales
- Margins: profit_margins, operating_margins, gross_margins
- Growth: quarterly_revenue_growth_yoy
- Balance Sheet: total_cash, total_debt, debt_to_equity, current_ratio
- Returns: return_on_equity
- Meta: sector, industry, beta

**Purpose:** LLM reads this JSON output and creates `{TICKER}_fundamental_analysis.md` markdown file

---

### generate_technical.py

Generate technical analysis data for LLM consumption (creates structured text output).

**Usage:**
```bash
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TCOM
```

**Output:** Structured text format with all technical indicators organized by section:
- Price Action (52-week range, position)
- Moving Averages (SMA, EMA, DEMA, TEMA, etc.)
- Momentum Indicators (RSI, MACD, Stochastic)
- Volatility (ATR, Bollinger Bands)
- Volume Analysis (OBV, A/D, volume trends)
- Support & Resistance (levels, nearest S/R)
- Trend Analysis (direction, strength, MA alignment)
- Advanced Indicators (ADX, Aroon, CCI, MFI, Williams %R)
- Fibonacci Retracements
- Pivot Points (classic and Fibonacci)
- Statistical Metrics (beta, correlation, volatility)
- Cycle Indicators

**Purpose:** LLM reads this structured output and creates `{TICKER}_technical_analysis.md` markdown file

**Note:** Do NOT pipe this to JSON - the output is human-readable text for LLM parsing.

---

### technical_indicators.py

Utility module for indicator calculations (imported by generate_technical.py).

**Note:** This is a utility module, not run directly. Used by generate_technical.py.

**Indicators Calculated:**
- Moving Averages: SMA (10, 20, 50, 100, 200), EMA, DEMA, TEMA
- Momentum: RSI, MACD, Stochastic, CCI, Williams %R
- Volatility: Bollinger Bands, ATR, ATR%
- Volume: OBV, AD, AD Oscillator
- Trend: ADX, DMI, Aroon
- Levels: Support/Resistance, Pivot Points, Fibonacci
- Statistics: Beta, correlations, volatility

---

## File Structure

### Price Data Location
**Path:** `prices/{TICKER}.csv`

**Format:**
```csv
Date,Open,High,Low,Close,Volume,Dividends,Stock Splits
2024-01-16,36.622,37.0201,36.2041,36.3732,3203000,0.0,0.0
2024-01-17,35.5174,35.8358,35.1691,35.7363,3048400,0.0,0.0
...
```

### Analytics Location
**Path:** `analytics/{TICKER}/`

**Files:**
- `{TICKER}_technical_analysis.md` - Technical analysis (LLM-created from price CSV)
- `{TICKER}_fundamental_analysis.md` - Fundamental analysis (LLM-researched)
- `{TICKER}_investment_thesis.md` - Investment thesis (LLM-analyzed)

**Note:** Analytics markdown files are created by LLM analysis, not by scripts. Scripts only manage price data.

---

## Data Integrity

**Important Rules:**
1. **Never manually edit price CSV files** - All price data must come from yfinance API
2. **Use scripts for all price operations** - Don't manually create or modify CSV files
3. **LLM creates analytics markdown** - Scripts don't create markdown files
4. **Incremental updates** - Running fetch_prices.py multiple times is safe (only adds new data)

---

## Workflow Examples

### Example 1: Analyze a New Stock
```bash
# 1. Fetch price data
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TCOM

# 2. Run /analyze command (orchestrates LLM analysis)
/analyze TCOM

# OR manually generate data for LLM:
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TCOM
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TCOM

# 3. LLM creates markdown files from price/fundamental data
# - analytics/TCOM/TCOM_technical_analysis.md
# - analytics/TCOM/TCOM_fundamental_analysis.md
# - analytics/TCOM/TCOM_investment_thesis.md
```

### Example 2: Update Existing Analysis
```bash
# 1. Fetch latest prices (incremental update)
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker NVDA

# 2. Generate latest technical and fundamental data
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker NVDA
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker NVDA

# 3. LLM updates analysis markdown files with new data
# (LLM reads structured outputs and updates analytics/NVDA/)
```

### Example 3: Quick Price Check
```bash
# Get current price only
python .claude/skills/analytics_generator/scripts/get_price.py --ticker AAPL

# Get historical prices for analysis
python .claude/skills/analytics_generator/scripts/get_prices.py --ticker AAPL --period 3M
```

---

## Troubleshooting

**Problem:** Script fails with "No module named 'yfinance'"
**Solution:** Install dependencies: `pip install yfinance pandas`

**Problem:** Price data is outdated
**Solution:** Run `fetch_prices.py` again - it will incrementally update

**Problem:** CSV file is corrupted
**Solution:** Delete the CSV file and run `fetch_prices.py` to re-download

**Problem:** Analytics markdown files don't exist
**Solution:** Run `/analyze [TICKER]` command to create them, or manually run:
```bash
# 1. Fetch prices
python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker TICKER

# 2. Generate technical and fundamental data
python .claude/skills/analytics_generator/scripts/generate_technical.py --ticker TICKER
python .claude/skills/analytics_generator/scripts/get_fundamental.py --ticker TICKER

# 3. LLM creates markdown files from the structured outputs
```
