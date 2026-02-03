# Scoring Systems Guide

Complete guide to the dual scoring system for stock analysis: **Quality Compounder** (Core) vs **Multi-Bagger Hunter** (Satellite).

**Updated: January 29, 2026**

---

## Quick Reference

| Attribute | Quality Compound | Multi-Bagger Hunter |
|-----------|------------------|---------------------|
| **Goal** | 15-30% CAGR | 5-10x potential |
| **Risk** | Low/Medium | High/Binary |
| **Time** | 5-10 years | 3-7 years |
| **Position** | 10-20% max | 2-5% max |
| **Success** | High batting avg | Slugging % |
| **Script** | `quality_compound_scorer.py` | `multibagger_hunter_scorer.py` |

---

## System Architecture

### Two-Stage Decision Framework

**Stage 1: STRATEGIC SCORE** (What to Buy)
- Determines IF the asset is worth owning
- Focus: Business quality, competitive moat, upside potential
- Components: Thesis + Fundamentals + Upside

**Stage 2: TACTICAL MODIFIER** (When to Buy)
- Determines entry timing and strategy
- Focus: Technicals, risk/reward setup
- Does NOT reduce Strategic Score

**Key Principle:** A great company with a bad chart = Opportunity (DCA), not Avoid.

---

## 1. Quality Compound Scorer

### Philosophy
Buying dollar bills for 50 cents, or buying great businesses at fair prices. Focus on the "Engine of Compounding."

### Gatekeepers (Must Pass All)

| Gatekeeper | Threshold | Reason |
|------------|-----------|--------|
| Market Cap | > $2B | Avoids micro-cap volatility |
| Operating Cash Flow | Positive (3 years) | Financial health |
| Interest Coverage | > 4x | No debt spirals |

**If ANY gatekeeper fails:** Stock still scores but marked with gatekeeper failure warning.

### Scoring Components (UPDATED Jan 2026)

| Component | Weight | Key Metrics |
|-----------|--------|-------------|
| **Moat & Power** | 30% | Pricing power, switching costs, network effects |
| **Fundamentals** | 25% | ROIC >15%, FCF/Net Income >0.8, margins |
| **Growth Quality** | 20% | Sustainable 15-30% CAGR |
| **Valuation** | 15% | PEG <2.0, FCF yield vs treasury |
| **Management** | 10% | Buybacks, dividends, capital allocation |

### Quality Classifications

| Type | Description | Examples | Exit Trigger |
|------|-------------|----------|--------------|
| **CAPITAL_CANNIBAL** | Aggressive buybacks reduce float >3% annually | AutoZone, Apple | P/E expands 50% above historical OR buyback paused |
| **THE_FRANCHISE** | Dominant market share, raises prices above inflation | Microsoft, Moody's | Market share decline >2% OR pricing power erodes |
| **THE_STALWART** | Lower growth (8-12%) but high dividend + safety | J&J, PepsiCo | Dividend cut OR fundamental degradation |

### Score Interpretation

| Quality Score | Compound Potential | Volatility | Time Horizon |
|---------------|-------------------|------------|--------------|
| 85-100 | 25-30% CAGR | Low | 5-10 years |
| 75-84 | 20-25% CAGR | Low-Medium | 5-10 years |
| 65-74 | 15-20% CAGR | Medium | 3-7 years |
| 55-64 | 10-15% CAGR | Medium | 2-5 years |
| 45-54 | 5-10% CAGR | Medium-High | 1-3 years |
| Below 45 | <5% or negative | High | Avoid |

### Common Pitfalls

1. **Value Trap:** Stock looks cheap (P/E 8x) but revenue is shrinking -3% annually
   - Rule: Never buy a compounder with negative organic growth just because it's "cheap"
   - Fix: Verify Moat score. If Moat < 60, it's a trap

2. **Thesis Creep:** Buying for short squeeze, holding as "value play"
   - Rule: Never switch buckets mid-investment
   - Fix: Multi-bagger breaks momentum → sell it, don't convert to compounder

---

## 2. Multi-Bagger Hunter Scorer

### Philosophy
Venture capital in public markets. Seeks S-Curve adoption phases where the market underestimates the magnitude of a shift.

### Gatekeepers (Must Pass All)

| Gatekeeper | Threshold | Reason |
|------------|-----------|--------|
| Liquidity | Daily Dollar Volume > $2M | Must be able to exit |
| Solvency | Cash Runway > 12 months OR Path to Profitability < 18 months | Bankruptcy risk |
| Trend | Price above 200-day MA | Don't catch falling knives |

### Scoring Components (UPDATED Jan 2026)

| Component | Weight | Key Metrics |
|-----------|--------|-------------|
| **Innovation Moat** | 25% | Proprietary IP, patent cliff, "un-copyable" tech |
| **TAM & Optionality** | 20% | Total Addressable Market > $50B (reduced from 25%) |
| **Founder/Vision** | 20% | Founder-led, >10% ownership, skin in the game |
| **Hyper-Growth** | 20% | Revenue growth >30% YoY, accelerating (NEW) |
| **Unit Economics** | 15% | Gross margins expanding, LTV/CAC > 3 (NEW) |

**Key Changes:**
- **TAM reduced** from 25% to 20% - capital efficiency is more important in high-rate environment
- **Hyper-Growth added** at 20% - growth rate is critical for multi-baggers
- **Unit Economics added** at 15% - the model must work at scale

### Phenomenon Classifications

| Type | Description | Ideal Entry | Exit Trigger |
|------|-------------|-------------|--------------|
| **HYPE_MACHINE** | Revolutionary tech + retail momentum | Breakout from consolidation | Trailing stop 20-30% OR growth decelerates 2 quarters |
| **CATEGORY_KING** | Winner-takes-most (Network Effects) | Market share crosses 15-20% | Network effect slows OR competitor reaches parity |
| **TURNAROUND** | New CEO/Strategy or Cycle shift | First "beat and raise" quarter | Turnaround fails OR re-rating complete |
| **EARNINGS_MACHINE** | Compounding with re-rating potential | Before discovery (score improving) | Valuation extended OR fundamental degradation |
| **PRODUCT_LAUNCH** | Binary outcome on single product | Pre-launch or at approval | Product fails OR post-launch success |
| **HIDDEN_GEM** | Micro-cap ignored by institutions | Post-IPO lockup expiration | Institutional coverage begins |

### Score Interpretation

| MB Score | Upside Potential | Binary Risk | Time Horizon |
|----------|-----------------|-------------|--------------|
| 85-100 | 10-20x | High | 5-10 years |
| 75-84 | 7-10x | High | 3-7 years |
| 65-74 | 5-7x | Medium-High | 3-5 years |
| 55-64 | 3-5x | Medium | 2-4 years |
| 45-54 | 2-3x | Medium | 1-3 years |
| Below 45 | <2x | High | Avoid |

### Common Pitfalls

1. **Dilution Death Spiral:** Revenue grows 50%, but share count grows 60%
   - Rule: Always check Revenue per Share growth, not just headline Revenue
   - Fix: If share count dilution >15% annually, disqualify or reduce score by 50%

2. **TAM Blindness:** $100B TAM but no path to capture meaningful share
   - Rule: TAM means nothing without distribution advantage
   - Fix: Require Innovation Moat >70 for TAM >$50B to count

---

## 3. Decision Matrix

### Strategic Score (Buy Decision)

| Strategic Score | Classification | Action |
|----------------|---------------|--------|
| 80-100 | Generational | BUY. If Technicals weak, start DCA |
| 65-79 | Investable | BUY. Standard position size |
| 50-64 | Watchlist | WAIT. Only buy if Technicals A+ |
| < 50 | Avoid | IGNORE. Fundamental thesis too weak |

### Entry Strategy Logic

1. **Strategic >= 65 + Tactical >= 70**: MOMENTUM ENTRY (Breakout)
2. **Strategic >= 80 + Tactical < 40**: AGGRESSIVE ACCUMULATION (Divergence = Opportunity)
3. **Strategic 65-79 + Tactical 40-69**: DCA / LIMIT ORDERS
4. **Strategic 50-64 + Tactical >= 80**: MOMENTUM PLAY (Lower conviction)
5. **Strategic < 50**: AVOID regardless of technicals

---

## 4. Which Scorer to Use?

| Investment Type | Scorer | Command |
|-----------------|--------|---------|
| Proven, profitable, compounding | Quality Compound | `quality_compound_scorer.py --ticker TICKER` |
| Speculative, early-stage, unprofitable | Multi-Bagger Hunter | `multibagger_hunter_scorer.py --ticker TICKER` |
| Mixed/unsure | Legacy LLM Scorer | `llm_scorer.py --ticker TICKER` |

### Decision Tree

```
Is it profitable (positive earnings)?
├─ Yes → Use Quality Compound Scorer
└─ No → Is TAM >$10B AND revenue growth >20%?
    ├─ Yes → Use Multi-Bagger Hunter
    └─ No → Use Legacy LLM Scorer
```

---

## 5. Implementation Examples

### Quality Compound: MSFT

```bash
python quality_compound_scorer.py --ticker MSFT

# Output:
# Ticker: MSFT | Quality Score: 82.3
# Type: THE_FRANCHISE (Pricing power, dominant market share)
# Compound Potential: 20-25% CAGR | Volatility: Low-Medium
# Fair Value: $520 | MoS: 8%
# Gatekeepers: PASSED
```

### Multi-Bagger: LAES (SEALSQ)

```bash
python multibagger_hunter_scorer.py --ticker LAES

# Output:
# Ticker: LAES | MB Score: 78.5
# Type: HYPE_MACHINE (Quantum security revolution)
# Upside: 7-10x | Risk: High
# 5x: $22.50 | 10x: $45.00
# Gatekeepers: PASSED
```

---

## 6. Exit Triggers by Strategy

### Quality Compound: Valuation-Based
- P/E expands 50% above historical average
- Fundamental degradation (ROE < 12%)
- Competitive moat erosion signs

### Multi-Bagger: Momentum-Based
- Trailing Stop Loss (20-30%) on momentum breakdown
- Growth decelerates for 2 consecutive quarters
- Fundamental thesis invalidated
- Time horizon exceeded without validation

---

## 7. Position Sizing Guidelines

| Strategy | Max Position | Rationale |
|----------|--------------|-----------|
| Quality Compound (80-100 score) | 10-20% | High conviction, low volatility |
| Quality Compound (65-79 score) | 5-10% | Good conviction, moderate volatility |
| Multi-Bagger (85-100 score) | 3-5% | High upside, binary risk |
| Multi-Bagger (65-84 score) | 1-3% | Moderate upside, high risk |

**Portfolio Allocation Target:**
- Quality Compound: 60-80% of portfolio
- Multi-Bagger: 20-40% of portfolio

---

## 8. Usage Examples

### Quality Compound Scorer

```bash
# Score a quality compounder
python .claude/skills/analytics_generator/scripts/quality_compound_scorer.py --ticker MSFT

# Batch score multiple
python .claude/skills/analytics_generator/scripts/quality_compound_scorer.py --tickers MSFT,AAPL,GOOGL --output quality_scores.json
```

### Multi-Bagger Hunter

```bash
# Score a speculative multibagger
python .claude/skills/analytics_generator/scripts/multibagger_hunter_scorer.py --ticker LAES

# Batch score speculative positions
python .claude/skills/analytics_generator/scripts/multibagger_hunter_scorer.py --tickers LAES,RZLV,PONY --output multibagger_scores.json
```

---

## 9. Common Mistakes to Avoid

### Quality Compound Scorer
1. **Don't** chase momentum - quality compounders should be bought on valuation
2. **Don't** overpay for growth - P/E >30 for 20% growers is expensive
3. **Don't** ignore moat erosion - competitive advantages decay
4. **Don't** buy negative organic growth just because it's "cheap"

### Multi-Bagger Hunter
1. **Don't** over-position any single stock - max 5% position
2. **Don't** expect linear returns - volatility is expected
3. **Don't** fall in love with the story - maintain exit discipline
4. **Don't** ignore runway - companies running out of cash go to zero
5. **Don't** ignore dilution - check Revenue Per Share, not just Revenue

---

*Last Updated: January 29, 2026*
