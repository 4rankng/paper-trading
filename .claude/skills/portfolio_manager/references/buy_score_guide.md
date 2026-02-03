# Buy Score Calculation Guide

Comprehensive guide for calculating each component of the buy score (0-100).

## The Formula

```
Buy Score = (Thesis × 0.40) + (Fundamental × 0.30) + (Expected Return × 0.30)
```

**Weight Rationale (NEW - Jan 2026):**
- **Thesis (40%)**: Primary driver - catalysts, moat, sector tailwinds matter most
- **Fundamental (30%)**: Financial health validates the business model
- **Expected Return (30%)**: 1-year upside based on fair value estimation
- **Technical (0%)**: Removed - timing noise, not relevant for long-term investment decisions
- **Volume (0%)**: Removed - short-term noise

## Score Classification

| Total Score | Classification | Action |
|-------------|----------------|--------|
| 75+ | Strong Buy | BUY - Top conviction |
| 60-74 | Buy | BUY - Standard entry |
| 50-59 | Moderate Buy | WATCH - Wait for better entry |
| 40-49 | Weak | WATCH - Low priority |
| <40 | Avoid | AVOID - Poor setup |

## Component Scoring

### 1. Thesis Strength (35%) - PRIMARY DRIVER

Score: 0-100 | Base: 50, adjusted by thesis quality

**Scoring Formula:**

```
Base = 50
+10 if thesis file exists
+4 per catalyst (max +20 for 5+ catalysts)
+10 if "clear moat" identified
+10 if action=BUY, -20 if action=AVOID
+10 if fit >80%, +5 if fit >70%
```

**Thesis Quality Assessment:**

| Element | Strong | Weak |
|---------|--------|------|
| **Catalysts** | 3+ near-term catalysts with dates | Vague future events |
| **Moat** | Clear competitive advantage (brand, IP, network) | No differentiation |
| **Sector Tailwinds** | Strong secular trend | Declining industry |
| **Management** | Proven track record, founder-led | Unknown or poor history |
| **Valuation Context** | Clear fair value estimate | No valuation framework |

**Catalyst Examples (each +4):**
- Product launches (FDA approval, new chip release)
- Earnings inflection points
- M&A activity
- Regulatory changes (CNSA 2.0, CHIPS Act)
- Major customer wins
- Industry conferences/events

---

### 2. Fundamentals (25%)

Score: 0-100 | Base: 50, adjusted by metrics

**Scoring Formula:**

```
Base = 50
+20 if net_margin > 20%, +10 if >10%, +5 if >0%, -10 if negative
+15 if ROE >20%, +10 if >15%, +5 if >10%
+10 if debt/equity <50%, +5 if <100%, -10 if >200%
+20 if revenue_growth >50%, +15 if >30%, +10 if >15%, +5 if >5%
+10 if strong cash position (speculative stocks)
+10 if profitable, -5 if unprofitable without high growth
```

**Quick Reference:**

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| Net Margin | >20% | 10-20% | 0-10% | Negative |
| ROE | >20% | 15-20% | 10-15% | <10% |
| Debt/Equity | <50% | 50-100% | 100-200% | >200% |
| Revenue Growth | >50% | 30-50% | 15-30% | <15% |
| P/E (TTM) | <15x | 15-25x | 25-50x | >50x |

---

### 3. Risk/Reward (15%)

Score: 0-100 | Based on R:R ratio from thesis or watchlist

**Scoring Formula:**

```
R:R = (exit - price) / (price - stop)

R:R >= 3.0: Score = 100 (Excellent)
R:R >= 2.0: Score = 80  (Good)
R:R >= 1.5: Score = 65  (Fair)
R:R >= 1.0: Score = 45  (Poor)
R:R < 1.0:  Score = 20  (Negative)
```

**R:R Quality Guide:**

| R:R Ratio | Quality | Position Size Implication |
|-----------|---------|---------------------------|
| 3:1+ | Excellent | Full position |
| 2:1+ | Good | Standard position |
| 1.5:1+ | Fair | Reduced size |
| <1.5:1 | Poor | Pass or very small |

---

### 4. Technical Strength (15%)

Score: 0-100 | Source: `aggregate_signals.py`

**Five Categories Aggregated:**

| Category | Indicators | Scoring |
|----------|------------|---------|
| **Momentum** | RSI, MACD, Stochastic, Williams %R, CCI, MFI, ROC | RSI <30 bullish, >70 bearish |
| **Trend** | ADX, Aroon, MA crossovers, MA slopes, Parabolic SAR | ADX >25 + uptrend = bullish |
| **Volatility** | ATR%, Bollinger Bandwidth, 30-day vol std | Low vol = squeeze (bullish) |
| **Volume** | Volume ratio, OBV trend, A/D line, PV correlation | Vol ratio >1.5 = bullish |
| **OB/OS** | Stochastic OB/OS, 52-week range, BB position | Near 52-week low = bullish |

**Quick Manual Scoring:**

| Technical Condition | Score |
|--------------------|-------|
| Strong uptrend, all MAs aligned, ADX >25, RSI 50-70 | 75-90 |
| Uptrend, price above MA50/200, positive momentum | 60-74 |
| Sideways, price between MAs, mixed signals | 45-59 |
| Downtrend, price below key MAs, negative momentum | 30-44 |
| Strong downtrend, selling pressure, breakdowns | 0-29 |

**Important:** Technical is ENTRY TIMING only. A low technical score (30-40) with strong thesis/R:R is still a valid buy - just wait for pullback.

---

### 5. Volume Pattern (10%)

Score: 0-100 | Extracted from volume category in technical analysis

**What to Look For:**

| Pattern | Score | Description |
|---------|-------|-------------|
| Strong Accumulation | 80-100 | Vol ratio >1.5, OBV rising, price up on vol |
| Moderate Accumulation | 60-79 | Vol ratio >1.2, positive OBV trend |
| Neutral | 40-59 | Average volume, flat OBV |
| Distribution | 20-39 | Vol ratio <0.8, OBV falling, price down on vol |
| Heavy Distribution | 0-19 | High volume selling, declining OBV |

---

## Example: VKTX Full Calculation (Corrected Weights)

```
Thesis (35%):      90 × 0.35 = 31.5
  - Has thesis (+10), 5 catalysts (+20), High fit (+10) = Base 90

Fundamental (25%):  50 × 0.25 = 12.5
  - Base 50, strong cash (+5), unprofitable (-5) = 50

Risk/Reward (15%): 100 × 0.15 = 15.0
  - Excellent R:R 5.1:1 from thesis

Technical (15%):    37 × 0.15 =  5.6
  - Weak current signal, but thesis > technical

Volume (10%):       37 × 0.10 =  3.7
  - From signal score

TOTAL = 31.5 + 12.5 + 15.0 + 5.6 + 3.7 = 68.3 → Buy
```

**Key Insight:** VKTX scores 68.3 despite weak technicals because thesis (35%) and R:R (15%) drive the decision. The low technical score just suggests waiting for a pullback entry, not avoiding the stock.

---

## Automation

Buy score is calculated via the `analytics_generator` skill:

```bash
# Calculate buy score for any ticker (LLM-based scoring)
python .claude/skills/analytics_generator/scripts/llm_scorer.py --ticker NVDA

# All watchlist stocks
python .claude/skills/analytics_generator/scripts/llm_scorer.py --all --min-score 60

# Output to file
python .claude/skills/analytics_generator/scripts/llm_scorer.py --all --output analytics/buy_scores.json

# For technical-only scoring (no LLM)
python .claude/skills/analytics_generator/scripts/aggregate_signals.py --ticker NVDA
```
