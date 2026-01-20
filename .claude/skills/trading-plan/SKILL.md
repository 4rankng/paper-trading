---
name: trading-plan
description: Generate concise trading plan with entry/exit/stop and confidence level. Optimized for scalping/day-trading (1d-5d holds) with technicals (80%) and sentiment (15%) as primary factors. Use for: "create trading plan for [TICKER]", "generate trading plan", "/trade [TICKER] [timeframe]". Outputs to trading-plans/ folder.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
  - Skill
---

# Trading Plan Skill

Generate concise, actionable trading plans with clear entry/exit/stop levels and confidence.

## Quick Start

```
User: "/trade NVDA 3m"
→ You: Invoke trading-plan skill
→ Step 1: Invoke trading-debate skill (7 agents for 3m timeframe)
→ Step 2: Read analytics files (technical primary, sentiment secondary)
→ Step 3: Use debate insights + analytics to craft plan
→ Step 4: Generate concise trading plan
→ Save to: trading-plans/NVDA/NVDA_YYYY_MM_DD_3m.md
```

**For Scalping/Day Trading (1d-5d):**
```
User: "/trade NVDA 1d"
→ Technical analysis (80%) + Sentiment (15%) + Fundamentals (5% guardrails)
→ Tight ATR-based stops (3-5%), quick targets (5-15%)
```

## Input

- **TICKER**: Stock symbol
- **TIMEFRAME**: Investment horizon (1m, 3m, 6m, 1y)
- **CAPITAL** (optional): Total portfolio value for dollar position sizing

## Timeframe Strategy

| Timeframe | Approach | Focus | Stop Type | Exit Strategy |
|-----------|----------|-------|-----------|---------------|
| **1d-5d** | Scalping/Day Trading | Technicals (80%) + Sentiment (15%) | Tight ATR-based (-3-5%) | Quick hits 5-15%, scale out |
| **≤1m** | Swing Trading | Technicals + Catalysts | Tight (-5-8%) | Scale out on 10-20% gains |
| **6m** | Position Trading | Catalyst-driven | Technical (-8-12%) | Scale out on 20-30% gains |
| **>1y** | Investment | Fundamentals + Value | Fundamental only | Hold until convergence |

## Scalping/Day Trading Priority (Primary Strategy)

**For 1d-5d holds, the factor weighting is:**

| Factor | Weight | What Matters |
|--------|--------|--------------|
| **Technical Analysis** | 70-80% | Price action, volume, support/resistance, RSI, EMAs |
| **Sentiment/Catalysts** | 15-20% | News flow, earnings, Fed decisions, short interest |
| **Fundamentals** | 5-10% | Guardrails only (avoid bankruptcies, fraud risk) |

**Core Principle:** At 1-5 day holds, you trade *other traders' reactions* — not business value. P/E ratios are irrelevant for scalping.

**Required Setup for Scalping:**
- **Liquidity:** Average daily volume > 2M shares (must enter/exit fast)
- **Volatility:** Beta > 1.2 or ATR > 3% of price (need movement for edge)
- **Clear technical levels:** Well-defined support/resistance
- **Near-term catalyst:** Earnings, data releases, events within 10 days |

---

## Dynamic Factor Weighting by Timeframe

**The shorter the timeframe, the more technicals dominate:**

| Timeframe | Technical | Sentiment | Fundamentals | Primary Focus |
|-----------|-----------|-----------|--------------|---------------|
| **1d-3d** (Scalping) | 80% | 15% | 5% | Price action, volume patterns |
| **3d-1w** (Day Trading) | 75% | 15% | 10% | Technical levels, intraday catalysts |
| **1w-1m** (Swing) | 60% | 25% | 15% | Momentum, short-term catalysts |
| **1m-3m** (Position) | 40% | 35% | 25% | Trend, sentiment shifts, valuation checks |
| **3m-6m** (Position) | 30% | 30% | 40% | Catalyst-driven, earnings trajectory |
| **6m-1y** (Long Position) | 20% | 25% | 55% | Earnings quality, sector trends |
| **1y+** (Investment) | 10% | 15% | 75% | Business value, moat, DCF |

**Key Rules:**
- **Technicals** = Directly observable (price, volume, indicators)
- **Sentiment** = Catalysts, news flow, social sentiment, short interest
- **Fundamentals** = Financial health, growth, valuation (minimal for scalping) |

## Prerequisites

**Macro Check:**
```bash
# Check current macro stance before any trading decision
ls -lt macro/theses/ | head -5
```

**Read latest macro thesis:** `macro/theses/macro_thesis_YYYY_MM.md`

- **HIGH macro risk** (recession, geopolitical crisis, systemic stress): Reduce position sizes, increase stops, delay entries
- **MEDIUM macro risk** (uncertainty, moderate volatility): Standard parameters
- **LOW macro risk** (stable growth, clear policy): Normal trading

**Data Freshness Check:**
```bash
ls -lh analytics/[TICKER]/
```

If missing or stale → Execute `/analyze [TICKER]` first.

## Process

### 0. Data Gap Detection

**Before generating any trading plan, check for data gaps using the `ask` skill.**

See [Data Gap Detection Workflow](references/data-gap-detection.md) for the complete process.

**Priority gaps for trading-plan:** Benchmark Gate questions (Q1-Q6), missing analytics.

### 0.5. Macro Risk Assessment

**Read latest macro thesis:** `macro/theses/macro_thesis_YYYY_MM.md`

**Assess macro risk level:**
- **HIGH** (Recession, war, systemic crisis): Reduce position size 50%, widen stops, consider delaying entry
- **MEDIUM** (Policy uncertainty, moderate volatility): Standard parameters
- **LOW** (Stable conditions): Normal trading

**Sector-specific macro check:** Review `macro/` folder for sector headwinds/tailwinds affecting the ticker.

---

### 1. Get Multi-Agent Insights

**Always:** Invoke `trading-debate` skill with [TICKER] and [TIMEFRAME]

The trading-debate skill will:
- Auto-select appropriate model based on timeframe:
  - ≤1m: Swing Trading (10 agents, 4 clusters)
  - 1m-6m: Position Trading (7 agents)
  - >1y: Investment (5 agents)
- Execute multi-agent analysis with adversarial debate
- Provide CIO synthesis with verdict and conviction

**Extract from debate output:**
- Verdict & Conviction (HIGH/MEDIUM/LOW)
- Vote tally (consensus strength)
- Bull case points (top 3)
- Bear case points (top 3)
- Risk/Reward assessment
- Key catalysts and risks
- Analyst consensus themes

**Use these insights to inform:**
- Machine classification validation
- Benchmark Gate decisions
- Rationale content
- Risk mitigation strategies
- Confidence level calibration

### 2. Read Analytics
- `analytics/[TICKER]/technical_analysis.md`
- `analytics/[TICKER]/fundamental_analysis.md`
- `analytics/[TICKER]/sentiment_analysis.md`

### 3. Phenomenon Classification (Timeframe-Driven)

**For 1d-5d (Scalping/Day Trading):**
- Default to **HYPE_MACHINE** (technical/sentiment-driven)
- Focus: Price action, volume patterns, short-term catalysts
- Stop: ATR-based technical breakdown
- Fundamentals: Guardrails only (avoid bankruptcy, fraud)

**For ≤1m timeframe:**
- Default to **HYPE_MACHINE** (technical/sentiment-driven)
- Focus: Short-term catalysts, technical setup, momentum
- Stop: Technical breakdown

**For 6m timeframe:**
- Classify as **HYPE_MACHINE** or **MEAN_REVERSION_MACHINE**
- Focus: Catalyst timeline, sentiment shifts, mean reversion
- Stop: Technical or thesis invalidation

**For >1y timeframe:**
- Default to **EARNINGS_MACHINE** (fundamental value)
- Focus: Intrinsic value, earnings growth, DCF
- Stop: Fundamental degradation only

### 4. Benchmark Gate (6 Tests)

| Test | Criteria | Result |
|------|----------|--------|
| Q1: Alpha Source | Specific edge (no "potential") | PASS/FAIL |
| Q2: Relative Strength | Beating sector ETF 3M? | PASS/FAIL |
| Q3: Institutional Footprint | Big Money buying? | PASS/FAIL |
| Q4: Anti-Catalyst | Clear 10-day runway? | PASS/FAIL |
| Q5: Expectation Gap | Sentiment not overheated? | PASS/FAIL |
| Q6: Exit Math | R:R ≥ 3:1? | PASS/FAIL |

**Decision:**
- PASS (≤1 fail) → Generate plan with BUY signal
- FAIL (≥2 fails) → Generate plan with AVOID signal

### 5. Generate Trading Plan (Timeframe-Tailored)

**File:** `trading-plans/[TICKER]/[TICKER]_YYYY_MM_DD_[TIMEFRAME].md`

**Timeframe-specific adjustments:**

**For 1d-5d (Scalping/Day Trading):**
- Position size: 0.25% max (higher risk of whipsaw)
- Stop loss: 3-5% (very tight, ATR-based)
- Target: 5-15% (quick hits)
- Focus: Technical setup, price/volume patterns, intraday catalysts
- Scale out: 50% at 5%, 50% at 10%
- **Liquidity check:** Position ≤ 1% of average daily volume
- **Volatility check:** Beta > 1.2 or ATR > 3% of price

**For ≤1m (Swing Trading):**
- Position size: 0.25% max (higher risk of whipsaw)
- Stop loss: 5-8% (tight, technical-based)
- Target: 10-20% (quick hits)
- Focus: Technical setup, short-term catalysts
- Scale out: 50% at 10%, 50% at 20%

**For 6m (Position Trading):**
- Position size: 0.5% max (moderate risk)
- Stop loss: 8-12% (technical or thesis invalidation)
- Target: 20-30% (catalyst-driven)
- Focus: Catalyst timeline, sentiment shifts
- Scale out: 40% at 20%, 40% at 30%, 20% hold for home run

**For >1y (Investment):**
- Position size: 1% max (fundamental conviction)
- Stop loss: Fundamental degradation only (ignore price volatility)
- Target: Intrinsic value convergence (50-100%+)
- Focus: DCF, earnings growth, value
- Hold until: Target reached or fundamentals degrade

**If CAPITAL provided:**
- Calculate dollar amount: `position_size × capital`
- Display both % and $ in plan (e.g., "0.5% ($500)")
- Use for liquidity check: Position ≤1% of average daily volume

**Structure:**
```markdown
# [TICKER] Trading Plan ([TIMEFRAME])

**Current Price:** $XX.XX
**Recommendation:** BUY/AVOID
**Machine:** [HYPE/EARNINGS/MEAN_REVERSION]
**Approach:** [Swing/Position/Investment] (based on timeframe)
**Confidence:** HIGH/MEDIUM/LOW (from debate conviction)
**R:R:** X:1

## Signal

**Entry:** $XX.XX
**Target:** $XX.XX (+X%)
**Stop:** $XX.XX (-X%)

**Position Size:** X% ($X,XXX)

## Rationale

[2-3 sentences max, tailored to timeframe]
- Incorporate top bull/bear points from debate
- Reflect consensus strength from vote tally
- Calibrate confidence level based on analyst conviction

## Machine Logic

**Why [MACHINE_TYPE] for [TIMEFRAME]:**
- [1 sentence]
- [1 sentence]

**Not other machines:**
- [1 sentence each]

## Catalysts

[Timeframe-appropriate catalysts]
- **Short-term:** [Date] - [Event]
- **Medium-term:** [Date] - [Event]
- **Long-term:** [Date] - [Event]

## Risk

**Top 3 Risks:**
1. [Risk from debate bear case] - [Mitigation from debate]
2. [Risk from debate bear case] - [Mitigation from debate]
3. [Risk from debate bear case] - [Mitigation from debate]

## Exit Triggers

- [Trigger]
- [Trigger]
- [Trigger]

**Generated:** YYYY-MM-DD
**Next Review:** YYYY-MM-DD
```

### 6. Correlation Check (if BUY signal)

Use `portfolio_manager` skill to check top 3 holdings.

**If correlated (HIGH):** Reduce position size or skip
**If correlated (MEDIUM):** Note in plan
**If correlated (LOW):** Proceed

### 7. Output Format

**Terminal:**
```markdown
## Trading Plan: [TICKER] ([TIMEFRAME])

**File:** trading-plans/[TICKER]/[TICKER]_YYYY_MM_DD_[TIMEFRAME].md
**Signal:** BUY/AVOID
**Entry:** $XX.XX | **Target:** $XX.XX | **Stop:** $XX.XX
**R:R:** X:1 | **Confidence:** HIGH/MEDIUM/LOW
**Position:** X% ($X,XXX)

[One-line rationale]

Full plan saved to file above.
```

## Constraints

- **Max 250 lines** per trading plan
- **Concise rationale:** 2-3 sentences max per section
- **No debate/analysis fluff** - just signals and logic
- **Entry rules apply to NEW BUYS only** (not existing holdings)
- **Never** apply Benchmark Gate to existing positions
- **Inertia Principle:** Existing holdings VALID unless proven DEAD
