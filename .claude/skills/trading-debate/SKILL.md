---
name: trading-debate
description: Multi-agent debate framework for trading decisions. Auto-selects model by timeframe: Scalping (6 agents, 1-7d), Swing (10 agents, 1-4w), Position (7 agents, 1-6m), Investment (5 agents, 1y+). Use for: "swing trade analysis", "trading debate", "multi-agent analysis", "investment outlook".
allowed-tools:
  - Read
  - Bash(python:*)
  - Bash(ls:*)
context: fork
agent: general-purpose
---

# Trading Debate Skill

Multi-agent adversarial analysis system for trading decisions. Automatically configures agent structure based on your timeframe.

## Quick Reference

| Timeframe | Model | Agents | Focus |
|-----------|-------|--------|-------|
| 1d-7d | Scalping/Day | 6 | Intraday momentum, quick exits |
| 1w-4w | Swing | 10 | Technical setups, short-term catalysts |
| 1m-6m | Position | 7 | Medium-term trends, catalyst-driven |
| 1y+ | Investment | 5 | Fundamentals, business quality |

## Prerequisites

**CRITICAL:** This skill requires FRESH analytics files (<24 hours old):
- `analytics/[TICKER]/[TICKER]_technical_analysis.md`
- `analytics/[TICKER]/[TICKER]_fundamental_analysis.md`
- `analytics/[TICKER]/[TICKER]_investment_thesis.md`

**Validate analytics before running:**
```bash
python .claude/skills/trading-debate/scripts/validate_analytics.py TICKER
```

If files are missing or stale, run `/analyze [TICKER]` first to refresh them.

## Timeframe Format

Timeframes use unit suffixes: `d` (days), `w` (weeks), `m` (months), `y` (years)

Examples: `3d`, `2w`, `6m`, `1y`

**Parse a timeframe:**
```bash
python .claude/skills/trading-debate/scripts/parse_timeframe.py 6m
```

## Agent Personas (Swing Model - 10 agents)

**Cluster 1: Environment** (Context)
- **Macro Strategist** - Rates, CPI, geopolitics (**CONTEXTUAL VETO**)
- **Sentiment & Flow** - Fear/greed, retail hype, institutional positioning

**Cluster 2: Strategists** (Thesis)
- **Trend Architect** - Momentum, EMA alignments, stage analysis
- **Mean-Reversion Specialist** - RSI, Bollinger Bands, exhaustion
- **Fundamental Catalyst** - Earnings quality, guidance

**Cluster 3: Evidence** (Validation)
- **Statistical Quant** - Standard deviations, volatility, probability
- **Tape Reader** - Price/volume divergence, smart money detection

**Cluster 4: Defense** (Guardians)
- **Short-Seller** - Red-teaming, structural flaws, bear case
- **Risk Manager** - R:R ratio, position sizing (**LINE-ITEM VETO**)

**Decision Maker**
- **Chief Investment Officer** - Synthesis, final grade, execution decision

For detailed persona descriptions, veto powers, and interactions, see [personas.md](references/personas.md).

## Additional Resources

- **Workflows:** See [workflows.md](references/workflows.md) for detailed execution flows for each model
- **Constraints:** See [constraints.md](references/constraints.md) for veto triggers, conviction tiers, and limits
- **Personas:** See [personas.md](references/personas.md) for detailed persona descriptions

## When to Use

**Use for:**
- Scalping/Day trading decisions (1-7 day holds)
- Swing trading decisions (1-4 week holds)
- Position trading decisions (1-6 month holds)
- Long-term investment analysis (1+ year horizon)
- Multi-perspective analysis with adversarial debate

**NOT for:**
- Portfolio management operations (use `portfolio_manager` skill)
- Existing holding reviews (use `position-review` skill)

## Output Location

Save ALL debate output to `trading-debates/[TICKER]/[TICKER]_YYYY_MM_DD_[TIMEFRAME].md`

Examples:
- `trading-debates/LAES/LAES_2024_05_15_6m.md` ✅
- `trading-debates/NVDA/NVDA_2024_05_15_1m.md` ✅
## Input Format

The debate compiles data from:
1. **Technical Analysis** - Trend, RSI, EMAs, support/resistance, volume, ATR
2. **Fundamental Analysis** - Market cap, valuation, growth, financial health
3. **Investment Thesis** - Phenomenon classification, thesis status, catalysts
4. **Recent news** - Latest 10 articles from `news/[TICKER]/`
5. **Portfolio context** - Current positions, cash, correlation risk

## Examples

### Example 1: Swing Trade Analysis
```
/debate NVDA 2w
```
- Loads 10-agent swing model
- Validates analytics freshness (<24h)
- Runs 4-phase workflow (Deep Analysis → Adversarial Debate → Confidence Vote → CIO Synthesis)
- Outputs to `trading-debates/NVDA/NVDA_2w_debate.md`

### Example 2: Long-Term Investment
```
/debate AAPL 1y
```
- Loads 5-agent investment model
- Focuses on fundamentals, moat, valuation
- Outputs to `trading-debates/AAPL/AAPL_1y_debate.md`

### Example 3: Scalping/Day Trade
```
/debate TSLA 3d
```
- Loads 6-agent scalping model
- Streamlined for rapid analysis
- Tight stops (1-1.5x ATR), quick targets

## Troubleshooting

### "Analytics files missing or stale"

**Cause:** Required analytics files don't exist or are >24 hours old.

**Solution:** Run `/analyze [TICKER]` to refresh all analytics files.

### "Veto triggered - no trade"

**Cause:** Risk Manager or Macro Strategist veto conditions met.

**Common veto triggers:**
- R:R < 3:1 (2:1 for day trades)
- Position size < 0.25%
- Portfolio correlation > 60%
- SPY below MA-200 AND VIX > 30 (bear market)

**Solution:** Accept the veto - the framework is protecting capital. No trade is better than a bad trade.

### "Low conviction - watch only"

**Cause:** Analyst votes split (5-6/9 for swing, 3-4/6 for position).

**Solution:** Add ticker to watchlist. Wait for more clarity or stronger signals.

### "Wrong model selected for timeframe"

**Cause:** Timeframe unit not recognized.

**Solution:** Use correct unit suffixes: `d`, `w`, `m`, `y`

### Debate output not saving

**Cause:** Incorrect output path.

**Solution:** Always save to `trading-debates/[TICKER]/` at project root, NOT in `.claude/skills/`

## Veto System (Non-negotiable)

### Risk Manager Veto (Line-Item - Absolute)
- R:R < 3:1 (2:1 for day trades)
- Position < 0.25%
- Correlation > 60%

### Macro Strategist Veto (Contextual)
- SPY below MA-200 AND VIX > 30
- Major event imminent (Fed, CPI)

**Important:** The CIO cannot override vetoes. Veto check happens BEFORE any synthesis.
