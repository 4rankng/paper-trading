# Strategy Classification Reference

Complete criteria for all trading strategies. Use this when analyzing a stock to determine its best-fitting strategy and fit score.

---

## Quick Reference

| Holding Period | Strategies | Data Sources |
|----------------|------------|--------------|
| `1-10d` | `gap_and_go`, `intraday_reversal`, `high_relative_vol` | Price/Volume (technical) |
| `2w-3m` | `trend_rider`, `mean_reversion`, `volatility_squeeze` | Price/Volume (technical) |
| `3-6m` | `canslim`, `golden_cross`, `turnaround` | Technical + Fundamentals |
| `3-12m` | `special_situation`, `binary_event`, `cyclical` | Catalyst/Event-driven |
| `1y+` | `quality_discount`, `dividend_aristocrat`, `quality_at_fair_price` | Fundamentals + Dividends |
| `until_value_opportunity` | `capital_preservation` | Risk-off/tactical |
| `conditional` | `conditional` | Catalyst-dependent |

---

## 1. Short-Term Strategies (1-10d)

**Focus:** Exploiting immediate supply/demand imbalances and momentum.

### gap_and_go

**Description:** Buying stocks that "gap" above the previous day's high at the open.

**Goal:** Capture the morning momentum driven by overnight news.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Gap Up | > 3% | 35 |
| Relative Volume (RVOL) | > 2.0 | 35 |
| Price | > $5.00 | 30 |

**Data Source:** Raw price CSV (`prices/{TICKER}.csv`)

**Calculation:**
```
Gap % = (Open - PrevClose) / PrevClose × 100
RVOL = Current Volume / 90-day Average Volume
```

---

### intraday_reversal

**Description:** Identifying stocks that have overextended and are "snapping back."

**Goal:** Profit from price exhaustion at key support/resistance levels.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| RSI (9) | < 30 (oversold) or > 70 (overbought) | 40 |
| Distance from VWAP | > 2% | 35 |
| Reversal candle | Hammer or Shooting Star | 25 |

**Data Source:** Technical analysis file or calculate from CSV

**Calculation:**
```
RSI = 100 - (100 / (1 + RS))
RS = Avg Gain / Avg Loss (over 9 periods)
VWAP distance = |Price - VWAP| / VWAP × 100
```

---

### high_relative_vol

**Description:** Scanning for stocks with unusual trading activity compared to their average.

**Goal:** Identify institutional entry or "smart money" movement.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Current Volume vs 90-day Avg | > 300% | 35 |
| Price Change | > 4% | 35 |
| Market Cap | > $300M | 30 |

**Data Source:** Raw price CSV + web search for market cap

**Calculation:**
```
Vol Ratio = Current Volume / 90-day Avg Volume × 100
Price Change = |Close - PrevClose| / PrevClose × 100
```

---

## 2. Swing Trading Strategies (2w-3m)

**Focus:** Catching the "meat" of a price move as it trends or cycles.

### trend_rider

**Description:** Entering stocks already in a confirmed uptrend.

**Goal:** Ride the prevailing momentum until a trend change occurs.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Price vs 20-day EMA | Above | 25 |
| Price vs 50-day EMA | Above | 25 |
| ADX (14) | > 25 | 25 |
| Higher Highs/Lows | Yes | 25 |

**Data Source:** Technical analysis file or calculate from CSV

**Calculation:**
```
EMA = Exponential Moving Average
ADX = Average Directional Index (trend strength)
Higher Highs: Current high > Previous high
```

---

### mean_reversion

**Description:** Betting that a price will return to its historical average.

**Goal:** Profit from "rubber band" effects when a stock is overstretched.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Price vs Bollinger Bands (20,2) | Below lower band | 40 |
| 10-day Price % Change | Deeply negative (< -5%) | 35 |
| Bollinger Band Width | Expanding | 25 |

**Data Source:** Technical analysis file or calculate from CSV

**Calculation:**
```
BB Lower = 20-day MA - (2 × 20-day SD)
10-day Change = (Close - Close[10]) / Close[10] × 100
```

---

### volatility_squeeze

**Description:** Identifying stocks where price action is narrowing (coiling).

**Goal:** Anticipate an explosive breakout following low volatility.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Bollinger Bands inside Keltner | Yes | 50 |
| ATR (14) | At multi-month lows | 50 |

**Data Source:** Technical analysis file or calculate from CSV

**Calculation:**
```
BB Width = (Upper - Lower) / Middle
Keltner = 20-day EMA ± (2 × ATR)
Squeeze: BB Upper < Keltner Upper AND BB Lower > Keltner Lower
```

---

## 3. Intermediate Growth Strategies (3-6m)

**Focus:** Combining fundamental excellence with technical confirmation.

### canslim

**Description:** William O'Neil's system for top-performing growth stocks.

**Goal:** Find "Super Performance" stocks before major price runs.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Quarterly EPS Growth | > 25% | 35 |
| Annual EPS Growth (3yr) | > 25% | 35 |
| Relative Strength (RS) | > 80 | 30 |

**Additional CANSLIM Factors:**
- **New:** New products, management, or 52-week highs
- **Supply/Demand:** Low float or high volume on breakouts
- **Institutional Sponsorship:** Increasing fund ownership
- **Market Direction:** General market in confirmed uptrend

**Data Source:** Fundamental analysis + web search for RS rating

---

### golden_cross

**Description:** 50-day SMA crossing above 200-day SMA.

**Goal:** Confirm major structural shift from bearish to bullish.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| 50-day SMA vs 200-day SMA | Crossed above | 50 |
| 200-day SMA Trend | Flattening or upward | 25 |
| Price vs 50-day SMA | Above | 25 |

**Data Source:** Calculate from raw price CSV

**Calculation:**
```
SMA50 = mean(Close[-50:])
SMA200 = mean(Close[-200:])
Golden Cross: SMA50 > SMA200 AND was below previously
```

---

### turnaround

**Description:** Companies undergoing operational or financial restructuring to improve performance.

**Goal:** Buy businesses before turnaround catalysts drive re-rating.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| New Management or Strategy | Yes | 35 |
| Declining Stabilizing | Yes | 35 |
| P/B Ratio | < 1.5 | 30 |

**Common Turnaround Triggers:**
- New CEO or leadership team
- Strategic pivot or refocusing
- Cost-cutting initiatives announced
- Asset sales or divestitures
- Debt restructuring completed

**Data Source:** News analysis, company filings

**Characteristics:**
- High risk, high potential reward
- Typically oversold due to past problems
- Catalyst-driven (earnings, strategic updates)
- 6-18 month timeframe for proof of turnaround

---

## 4. Event-Driven Strategies (3-12m)

**Focus:** Catalyst-driven opportunities with specific timelines.

### special_situation

**Description:** Investing in unique, time-limited corporate events or situations.

**Goal:** Capture returns from specific catalysts rather than general market trends.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Clear Catalyst Identified | Yes | 40 |
| Catalyst Timeline Defined | Yes | 30 |
| Risk/Reward Ratio | ≥ 2.0 | 30 |

**Common Special Situations:**
- Corporate spin-offs or split-offs
- M&A arbitrage opportunities
- Activist investor campaigns
- Restructuring or turnarounds
- Regulatory changes creating opportunities
- Litigation settlements
- IPO secondaries
- Bankruptcy reorganizations

**Data Source:** News analysis, SEC filings, corporate announcements

**Characteristics:**
- Returns driven by specific events with timelines
- Often uncorrelated with broader market
- Requires deep situational analysis
- Time-sensitive (catalyst has expected completion date)

---

### binary_event

**Description:** High-risk, binary outcome stocks where success or failure hinges on a single event or decision.

**Goal:** Speculative positions with asymmetric upside (10x+) but high risk of total loss.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Clear Binary Catalyst | Yes | 50 |
| Upside Potential | > 300% | 30 |
| Cash Position | Adequate to catalyst | 20 |

**Common Binary Events:**
- Clinical trial readouts (Phase 2/3)
- FDA/EMA approval decisions
- Legal verdicts (patent litigation)
- Regulatory rulings
- Licensing/bidding outcomes
- Bankruptcy survival

**Data Source:** News analysis, clinical trial registries, SEC filings

**Characteristics:**
- All-or-nothing outcomes
- Timeline to catalyst usually 3-12 months
- Position sizing critical (typically 1-2% max)
- Not suitable for risk-averse investors
- Often "lottery ticket" style opportunities

---

### cyclical

**Description:** Businesses whose earnings are highly correlated with economic or commodity cycles.

**Goal:** Buy at cycle bottom, sell at cycle peak. Requires timing and macro analysis.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| P/E at Cycle Low | < 12x | 40 |
| Deep Cyclical Industry | Yes | 35 |
| Cycle Position | Bottoming | 25 |

**Cyclical Industries:**
- Semiconductors
- Autos
- Chemicals
- Industrial metals
- Energy (E&P, services)
- Shipping/transportation
- Homebuilding
- Machinery

**Key Indicators:**
- P/E misleading at cycle peak (inverse relationship)
- Book value more reliable at peaks
- Capacity utilization rates
- Inventory-to-sales ratios
- Leading economic indicators

**Data Source:** Industry data, macro indicators, company filings

**Characteristics:**
- High volatility with economic cycles
- Requires macro timing skill
- Often trades at "cheap" multiples at peak
- Contrarian investing (buy when hated, sell when loved)

---

## 5. Long-Term Investing (1y+)

**Focus:** Value, compounding, and business quality.

### quality_at_fair_price

**Description:** High-quality businesses trading at reasonable valuations (not necessarily discounted).

**Goal:** Compound wealth over time by owning solid businesses at fair prices.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| ROE | > 15% | 40 |
| Debt/Equity | < 0.5 | 30 |
| P/E vs 5-year Avg | At or near average | 30 |

**Data Source:** Fundamental analysis or web search

**Calculation:**
```
ROE = Net Income / Shareholder Equity
D/E = Total Debt / Total Equity
P/E vs Avg = Current P/E ≈ 5-year Average P/E (±10%)
```

---

### quality_discount

**Description:** High-quality companies temporarily undervalued.

**Goal:** Maximize long-term ROI by "buying the dip" on blue chips.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| ROE | > 15% | 40 |
| Debt/Equity | < 0.5 | 30 |
| P/E vs 5-year Avg | Below average | 30 |

**Data Source:** Fundamental analysis or web search

**Calculation:**
```
ROE = Net Income / Shareholder Equity
D/E = Total Debt / Total Equity
P/E vs Avg = Current P/E < 5-year Average P/E
```

---

### dividend_aristocrat

**Description:** S&P 500 companies with 25+ years of dividend growth.

**Goal:** Generate reliable passive income and capital preservation.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Dividend Growth Streak | 25+ years | 40 |
| Payout Ratio | < 60% | 30 |
| Free Cash Flow | Positive | 30 |

**Data Source:** Web search (dividend history sites, Morningstar)

**Calculation:**
```
Payout Ratio = Dividends / Net Income × 100
FCF = Operating Cash Flow - Capital Expenditures
```

---

## 6. Capital Management (until_value_opportunity)

**Focus:** Risk-off positioning and tactical cash deployment.

### conditional

**Description:** Watchlist positions that depend on specific conditions being met before becoming actionable.

**Goal:** Track opportunities that require additional information or catalysts before investment decision.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Clear Condition Identified | Yes | 50 |
| Condition Timeline Defined | Yes | 30 |
| Risk/Reward If Triggered | ≥ 2.0 | 20 |

**Common Conditions:**
- Earnings report (guidance, inflection)
- Product launch/announcement
- Regulatory decision pending
- Legal ruling awaiting
- Management/strategic review completion
- Technical breakout/breakdown level
- Competitor/product catalyst

**Data Source:** News analysis, company guidance, technical levels

**Characteristics:**
- Pre-categorization for potential opportunities
- No action until condition is met
- Regular monitoring required
- May convert to active strategy or be removed
- Fit score typically 40-60 (potential, not confirmed)

**Example Conditions:**
- "Wait for Q3 earnings (Feb 4) - make-or-break for AI strategy"
- "Entry on breakout above $120 with volume confirmation"
- "Monitor pending FDA decision expected Q2"
- "Condition on SoftBank maintaining <35% ownership"

---

### capital_preservation

**Description:** Parking capital in low-risk instruments while waiting for better opportunities.

**Goal:** Protect principal during uncertain markets and maintain liquidity for future opportunities.

**Screening Criteria:**

| Criteria | Threshold | Weight |
|----------|-----------|--------|
| Liquidity | High (T-bills, money market) | 50 |
| Principal Risk | Minimal to none | 50 |

**Common Instruments:**
- Treasury bills (T-bills)
- Money market funds
- High-yield savings accounts
- Short-term CDs
- Commercial paper

**Data Source:** Brokerage account, treasury rates

**Characteristics:**
- Low/no return expectation (beat inflation modestly if lucky)
- High liquidity for quick deployment
- Ready capital for attractive opportunities
- Not an "investment" per se but a tactical allocation
- Fit score typically 40-60 (reflects tactical, not strategic, nature)

---

## Fit Score Calculation

For each strategy, calculate fit score as:

```
fit_score = (sum of met criteria weights) × 100
```

**Only assign a strategy if fit >= 60.**

If a stock scores below 60 on all strategies:
- `strategy: unclassified`
- `hold: unknown`
- `fit: 0`

---

## Data Sources & Calculation Guide

| Indicator | Source | Calculation Method |
|-----------|--------|-------------------|
| **From Price CSV** | | |
| 52-week high/low | `prices/{TICKER}.csv` | `max(Close[-252:])`, `min(Close[-252:])` |
| 20/50/200-day MA | CSV | `mean(Close[-N:])` |
| Golden Cross | CSV | `SMA50 > SMA200` |
| Gap % | CSV | `(Open - PrevClose) / PrevClose × 100` |
| Volume Ratio | CSV | `Volume[-1] / mean(Volume[-90:])` |
| Price Change | CSV | `(Close - Close[-1]) / Close[-1] × 100` |
| **From Technical Analysis** | | |
| RSI | `{TICKER}_technical_analysis.md` | RSI(9) or RSI(14) |
| ADX | Technical file | ADX(14) |
| Bollinger Bands | Technical file | BB(20,2) |
| VWAP | Technical file | Volume-weighted avg price |
| **From Fundamentals** | | |
| EPS, ROE, P/E | `{TICKER}_fundamental_analysis.md` | Company financials |
| **Web Search If Missing** | | |
| Market Cap | Web search | Shares × Price |
| Dividend History | Web search | Dividend sites |
| RS Rating | Web search | IBD, MarketSmith |
| Institutional Ownership | Web search | Yahoo Finance, 13F |

---

## Complete Data Gathering Workflow

1. **Check if `prices/{TICKER}.csv` exists** → fetch if missing
2. **Analyze raw CSV** for calculable indicators
3. **Check `{TICKER}_technical_analysis.md`** → generate if needed
4. **Check `{TICKER}_fundamental_analysis.md`** → generate if needed
5. **Web search** for data not available locally:
   - Market cap, RS rating, dividend history
   - Institutional ownership, debt metrics
6. **Classify** only when fit >= 60

---

## Web Search Templates

When local data is insufficient:

| Need | Search Query |
|------|--------------|
| Fundamentals | `"{TICKER} ROE PE ratio debt equity fundamentals"` |
| Dividends | `"{TICKER} dividend history payout ratio aristocrat"` |
| CANSLIM EPS | `"{TICKER} quarterly EPS growth earnings surprise"` |
| Institutional | `"{TICKER} institutional ownership percentage"` |
| Market Cap | `"{TICKER} market cap shares outstanding"` |
| RS Rating | `"{TICKER} relative strength rating IBD"` |
