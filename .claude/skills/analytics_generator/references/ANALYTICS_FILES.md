# Analytics Files Reference

Complete section structures for the analytics markdown files created during `/analyze` command execution.

## Overview

When invoked by `/analyze` command, the following files are created in `analytics/{TICKER}/`:

**Auto-Generated (Script-Created):**
1. **{TICKER}_signal_summary.md** - Technical Health Score, regime detection, signal aggregation

**LLM-Created:**
2. **{TICKER}_technical_analysis.md** - Price action, indicators, trends
3. **{TICKER}_fundamental_analysis.md** - Financials, business, risks
4. **{TICKER}_investment_thesis.md** - Thesis, catalysts, scenarios

---

## 0. Signal Summary (Auto-Generated)

**File:** `analytics/{TICKER}/{TICKER}_signal_summary.md`

**Focus:** Unified technical scoring from 40+ indicators (created by `aggregate_signals.py` script)

**Data Source:** Automatic calculation from price data

**Creation:** Script-generated, NOT created by LLM

### Sections (Auto-Generated)

1. **Market Regime**
   - Current regime: Trending Up/Down, Ranging, or Volatile
   - Regime confidence %
   - Supporting indicators (ADX, ATR%, Volatility Score, Trend Direction)

2. **Overall Technical Health Score**
   - Overall score (0-100) with classification
   - Category scores table:
     - Momentum (weight, score, classification)
     - Trend (weight, score, classification)
     - Volatility (weight, score, classification)
     - Volume (weight, score, classification)
     - OB/OS (weight, score, classification)
   - Signal convergence %
   - Confidence level (High/Medium/Low)

3. **Cross-Confirmation Analysis**
   - Bullish signals count and %
   - Bearish signals count and %
   - Neutral/Weak signals count
   - Divergence warnings (signals conflicting with overall trend)

4. **Key Signals**
   - Top 10 strongest signals by magnitude
   - Shows category, signal name, score, and classification

5. **Signal Dashboard** (Detailed by Category)
   - Momentum Signals table (all 14+ signals)
   - Trend Signals table (all 15+ signals)
   - Volatility Signals table (all 5 signals)
   - Volume Signals table (all 6 signals)
   - Overbought/Oversold Signals table (all 4 signals)

**Purpose for LLM:** Read this file FIRST to get quick technical overview. Use the Technical Health Score and confidence level to calibrate analysis. Refer to specific category scores when deep-diving into technical setup.

---

## 1. Technical Analysis (LLM-Created)

**File:** `analytics/{TICKER}/{TICKER}_technical_analysis.md`

**Focus:** Price action, indicators, trends (technical data from `generate_technical.py`)

**Data Source:** Structured output from `generate_technical.py` script

### Sections

1. **Price Action**
   - 52-week range (high, low, current position %)
   - Recent performance (1W, 1M, 3M, 6M, 1Y)
   - Price momentum indicators

2. **Moving Averages**
   - SMAs: 20, 50, 100, 200-day
   - EMAs: 12, 26, 50-day
   - Alignment analysis (bullish stack vs bearish stack)
   - Price vs MA relationships

3. **Momentum Indicators**
   - RSI (14-period: overbought/oversold levels)
   - MACD (signal, histogram, crossovers)
   - Stochastic (K, D, overbought/oversold)
   - CCI (Commodity Channel Index)
   - Williams %R

4. **Volatility**
   - ATR (Average True Range)
   - Bollinger Bands (width, squeeze, position)
   - Volatility regime (expansion vs contraction)

5. **Volume Analysis**
   - Volume trends (increasing/decreasing)
   - OBV (On-Balance Volume)
   - A/D Line (Accumulation/Distribution)
   - Volume profile analysis

6. **Support/Resistance**
   - Pivot highs/lows
   - Enhanced support/resistance zones
   - Fibonacci retracement levels
   - Psychological price levels

7. **Trend Analysis**
   - Trend direction (uptrend/downtrend/sideways)
   - Trend strength (ADX-based)
   - MA alignment (bullish/bearish/neutral)
   - Trendline analysis

8. **Advanced Indicators**
   - ADX (Average Directional Index)
   - Aroon Indicator
   - MFI (Money Flow Index)
   - Ultimate Oscillator

9. **Pattern Recognition**
   - Consolidation patterns
   - Stage analysis (accumulation, markup, distribution, markdown)
   - Setup identification

10. **Key Levels**
    - Support zones (price ranges)
    - Resistance zones (price ranges)
    - Pivot points (R1, R2, S1, S2)

11. **Statistical Metrics**
    - Beta vs market
    - Correlation with sectors/indices
    - Historical volatility metrics

12. **Summary & Trading Levels**
    - Overall technical assessment
    - Key support/resistance levels
    - Technical risk factors

---

## 2. Fundamental Analysis

**File:** `analytics/{TICKER}/{TICKER}_fundamental_analysis.md`

**Focus:** Current financial state, historical performance (company TODAY)

**Data Sources:** News articles (from `news/{TICKER}/` - MANDATORY), watchlist factors, research

### Sections

1. **Business Overview**
   - Products and services
   - Business model
   - Revenue streams
   - Geographic exposure

2. **Competitive Position**
   - Market share
   - Competitive moat
   - Competitive advantages
   - Industry ranking

3. **Current Financial Health**
   - **Income Statement**
     - Revenue trends
     - Gross margin, operating margin, net margin
     - Profitability trends
   - **Balance Sheet**
     - Debt levels (debt/equity, net debt)
     - Cash position
     - Share buybacks/dividends
   - **Cash Flow**
     - Operating cash flow
     - Investing cash flow (CapEx)
     - Financing cash flow

4. **Historical Financial Performance**
   - **Revenue Growth** (3-5 year trends)
     - CAGR calculation
     - Year-over-year comparisons
     - Growth acceleration/deceleration
   - **Margin History**
     - Expansion/contraction patterns
     - Operating leverage analysis
     - Margin vs peers
   - **Earnings Quality**
     - Earnings consistency
     - Beat/miss track record
     - Adjusted vs GAAP earnings
   - **Return on Capital**
     - ROIC trends
     - ROE trends
     - ROA trends

5. **Sector Position**
   - Industry ranking and market position
   - Relative strength vs sector peers
   - Market share trends

6. **Management Quality**
   - **Execution Track Record**
     - Historical performance vs promises
     - Strategic initiative success rate
   - **Capital Allocation History**
     - ROI on investments
     - Buyback timing and effectiveness
     - M&A success rate
   - **Corporate Governance**
     - Board structure
     - Executive compensation alignment

7. **Current Valuation Metrics**
   - **Multiples**
     - P/E (forward and trailing)
     - PEG ratio
     - P/S ratio
     - P/B ratio
     - EV/EBITDA
   - **Comparisons**
     - Valuation vs peers (current)
     - Historical valuation range (5-year)
     - Premium/discount analysis

8. **Financial Risks**
   - **Debt Profile**
     - Debt maturity schedule
     - Interest coverage ratio
     - Debt covenants
   - **Liquidity Risks**
     - Current ratio, quick ratio
     - Cash burn rate
   - **Accounting Quality**
     - Red flags (if any)
     - Revenue recognition policies
     - One-time items frequency

---

## 3. Investment Thesis

**File:** `analytics/{TICKER}/{TICKER}_investment_thesis.md`

**Focus:** Future outlook, growth drivers, scenarios (company TOMORROW)

**Purpose:** Data-driven insights only, NO trading recommendations

**Data Sources:** Technical + Fundamental + News (from `news/{TICKER}/` - MANDATORY) + Watchlist synthesis

### Sections

1. **Phenomenon Classification**
   - **Type:** HYPE_MACHINE / EARNINGS_MACHINE / MEAN_REVERSION_MACHINE
   - **Rationale:** Why this classification based on company stage and market dynamics

2. **Executive Summary**
   - 3-5 sentence overview of the investment thesis
   - Key opportunity and primary risks

3. **Future Growth Drivers**
   - **Revenue Growth Trajectory** (next 3-5 years projected)
     - Core business growth
     - New product contributions
     - Market expansion opportunities
   - **Margin Expansion Potential**
     - Operating leverage
     - Scale benefits
     - Cost reduction initiatives
   - **New Market Opportunities**
     - Geographic expansion
     - New product lines
     - Adjacent market entry
   - **Industry Tailwinds**
     - Sector growth trends
     - Market size expansion (TAM, SAM, SOM)
     - Regulatory/supportive changes

4. **Competitive Future Position**
   - **Moat Strength** (strengthening or erosion risks)
   - **Market Share Trajectory** (gain/lose/steady with rationale)
   - **Disruption Threats**
     - Technology disruption risk
     - Regulatory disruption risk
     - Competitive disruption risk

5. **Upcoming Catalysts (Timeline-Specific)**
   - **Product Launches**
     - Pipeline products
     - Launch dates/estimates
     - Expected revenue impact
   - **M&A Opportunities**
     - Potential targets
     - Strategic rationale
   - **Regulatory Changes**
     - Pending regulations
     - Impact assessment
   - **Earnings Dates & Guidance**
     - Next earnings date
     - Guidance expectations
   - **Industry Conferences/Events**
     - Upcoming events
     - Expected announcements

6. **Investment Scenarios (Future Outcomes)**

   **Base Case:** Likely range (X-Y%)
   - Rationale based on phenomenon type, confidence level, data quality, market conditions

   **Bull Case:** Possible range (X-Y%)
   - Rationale for upside scenario
   - Catalysts that would trigger this

   **Bear Case:** Possible range (X-Y%)
   - Rationale for downside scenario
   - Risk factors that would trigger this

   **Probability Calibration:**
   - Phenomenon type → affects uncertainty (HYPE = high uncertainty, EARNINGS = medium, MEAN_REVERSION = low)
   - Confidence level → affects base case skew (HIGH/MEDIUM/LOW)
   - Data quality → affects confidence (fresh/stale/complete/incomplete)
   - Market conditions → affects skew (bullish/bearish/neutral)

   **Expected Value Calculation:**
   - Weighted probability calculation
   - Risk-adjusted return expectation

7. **Thesis Validation Milestones**
   - **Key Metrics to Watch** (quarterly/annual)
     - Revenue growth rate
     - Margin metrics
     - Customer metrics
   - **Catalyst Checkpoints** (with dates)
     - Product launch milestones
     - Partnership announcements
   - **Early Warning Indicators** for thesis failure
     - Metric deterioration thresholds
     - Competitive loss signals

8. **Future Risks & Opportunities**
   - **Upside Opportunities** (blue sky scenarios)
     - Market expansion beyond base case
     - Technology breakthroughs
     - Strategic partnerships
   - **Downside Risks** (black swan events, thesis killers)
     - Technology disruption
     - Regulatory changes
     - Competitive encroachment
     - Management failure
   - **Mitigation Strategies** for key risks
     - Diversification
     - Monitoring approaches
     - Exit triggers

9. **Risk/Reward Analysis**
   - **Upside Potential** (% and price target)
     - Based on bull case
   - **Downside Risk** (% and stop loss level)
     - Based on bear case
   - **Risk/Reward Ratio**
     - Upside/downside comparison
     - Attractiveness assessment

10. **Key Levels to Monitor**
    - Support levels (technical)
    - Resistance levels (technical)
    - Breakdown signals (thesis failure)

11. **Catalyst Timeline**
    - **Near-term** (0-3 months)
      - Expected catalysts
      - Impact assessment
    - **Medium-term** (3-12 months)
      - Expected catalysts
      - Impact assessment
    - **Long-term** (12+ months)
      - Expected catalysts
      - Impact assessment

---

## Important Notes

**All three analytics files:**
- Are created by LLM analysis (not by scripts)
- Provide data-driven insights ONLY
- NO trading recommendations (BUY/SELL/HOLD) in analytics files
- Max 1000 lines per file (compress if exceeded)

**Trading recommendations** belong in `trading-plans/` folder (use `/trade` command).

**Signals** belong in `signals/` folder (use `signal-formatter` skill).
