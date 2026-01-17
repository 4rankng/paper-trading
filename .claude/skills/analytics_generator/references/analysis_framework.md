# Stock Analysis Criteria Framework

This document defines the comprehensive analysis framework for stock evaluation.

## File Structure

Analytics are saved as **three separate markdown files** in `analytics/{TICKER}/`:

1. **`{TICKER}_technical_analysis.md`** - All technical indicators and price action analysis
2. **`{TICKER}_fundamental_analysis.md`** - Business fundamentals, financial metrics, competitive position
3. **`{TICKER}_investment_thesis.md`** - Investment thesis, scenarios, validation tracking, catalysts

**Data Pipeline:**
1. `fetch_prices.py` → `prices/{TICKER}.csv` (OHLCV price data)
2. `generate_technical.py` → Structured text output (for LLM consumption)
3. **LLM** → Creates/updates the 3 markdown files above

**Important:** LLM creates markdown files, not scripts. Scripts provide DATA only.

## Analysis Sections by File

### `{TICKER}_technical_analysis.md`

**Content:** All technical indicators calculated from price data using `generate_technical.py`

**Sections:**
1. **Price Action** - 52-week range, current position, recent performance
2. **Moving Averages** - All SMAs (10, 20, 50, 100, 200), EMAs (20, DEMA, TEMA), advanced MAs (T3, WMA, KAMA, MAMA, FAMA, SAR)
3. **Momentum Indicators** - RSI (14), MACD, Stochastic, CCI, MFI, Williams %R, Ultimate Oscillator
4. **Volatility** - ATR, ATR%, Bollinger Bands, volatility regime
5. **Volume Analysis** - Trends, OBV, A/D, accumulation/distribution patterns
6. **Support & Resistance** - Multiple methods (pivot highs/lows, enhanced, Fibonacci)
7. **Trend Analysis** - Direction, strength, MA alignment, trendline analysis
8. **Advanced Indicators** - ADX, Aroon, cycle indicators
9. **Pattern Recognition** - Consolidation, stages, setups
10. **Key Levels** - Support zones, resistance zones, pivot points
11. **Statistical Metrics** - Beta, correlations, volatility
12. **Summary & Trading Levels** - Support, resistance, targets

**Technical Score:** 0-100 based on indicator alignment

---

### `{TICKER}_fundamental_analysis.md`

**Content:** Business fundamentals and financial health (LLM-researched)

**Sections:**
1. **Business Overview** - What they do, products/services, business model
2. **Competitive Position** - Market share, moat, competitive advantages
3. **Financial Metrics** - P/E, PEG, revenue growth, margins, profitability ratios
4. **Balance Sheet** - Debt levels, cash position, buybacks, dividends
5. **Growth Trajectory** - Historical growth, projected growth, catalysts
6. **Sector Position** - Industry trends, relative strength vs sector/peers
7. **Key Risks** - Regulatory, competitive, operational, financial risks
8. **Opportunities** - Market expansion, product launches, M&A potential
9. **Management Quality** - Execution track record, capital allocation
10. **Valuation vs Peers** - P/E, PEG, P/S, P/B comparisons

**Fundamental Score:** 0-100 based on financial health and growth

---

### `{TICKER}_investment_thesis.md`

**Content:** Investment thesis, scenarios, and validation tracking (LLM-synthesized)

**Sections:**
1. **Phenomenon Classification** - HYPE_MACHINE / EARNINGS_MACHINE / MEAN_REVERSION_MACHINE
2. **Executive Summary** - 3-5 sentence overview of opportunity/risks
3. **Core Investment Thesis** - Bull/bear case in 1-2 paragraphs
4. **Key Catalysts** - Timeline-specific events (earnings, product launches, regulatory)
5. **Investment Scenarios**
   - Base case (60% probability)
   - Bull case (25% probability)
   - Bear case (15% probability)
   - Expected value calculation
6. **Thesis Validation** - Checklist with milestones to track
7. **Risk/Reward Analysis**
   - Upside potential (% and price target)
   - Downside risk (% and stop loss level)
   - Risk/reward ratio
   - Position sizing recommendation
8. **Key Levels to Monitor** - Support levels, resistance levels, technical breakdown signals
9. **Actionable Intelligence** - For existing positions (HOLD/TRIM/ADD) or new analysis (BUY/AVOID)
10. **Catalyst Timeline** - Near/medium/long-term dates to watch

---

## Important Notes

- **No auto-generated buy/sell recommendations**: Analytics files contain facts and analysis only. Recommendations come from skills that process this data (position-review, investment-workflow).
- **LLM-created content**: All 3 markdown files are created by LLM analysis, not by scripts
- **Scripts provide data only**: `fetch_prices.py` and `generate_technical.py` provide raw data for LLM consumption
- **Data-driven**: Conclusions should be supported by data and evidence
- **Regular updates**: Re-run `/analyze [TICKER]` to update with latest price data and news
