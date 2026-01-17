# Trading Debate Constraints Reference

Detailed constraints, veto powers, and decision thresholds for each trading model.

---

## Scalping/Day Trading Constraints (1d - 7d)

**Position Sizing:**
- Maximum: 0.25-0.5% of portfolio
- Minimum: 0.25% (Risk Manager veto if below)

**Hold Period:**
- Target: 1-7 days
- Often intraday to overnight
- Time stop: Exit EOD if no movement

**Stop-Loss:**
- Tight hard stop: 1-1.5x ATR
- No trailing stops (quick entries, quick exits)

**Risk/Reward:**
- Minimum: 2:1 (lowered for quick trades)
- Target: 2-3% moves

**Earnings:**
- Exit before earnings unless day-of event

### Conviction Tiers

| Bullish Votes | Conviction | Position Size |
|--------------|------------|---------------|
| 5/5 | High | 0.5% |
| 4/5 | Medium | 0.35% |
| 3/5 | Low | 0.25% |
| <3/5 | Avoid | 0% |

### Veto Triggers (Non-negotiable)

**Risk Manager (Line-Item Veto):**
- R:R < 2:1
- Position size < 0.25%
- Portfolio correlation > 60%

---

## Swing Trading Constraints (1w - 4w)

**Position Sizing:**
- High Conviction: 0.5-1%
- Speculative: 0.25-0.5%
- Minimum: 0.25%

**Hold Period:**
- Target: 1-4 weeks
- Time stop: Re-evaluate if no movement after 7 days

**Stop-Loss:**
- Hard stop based on ATR (typically 2x ATR)
- No trailing stops for swing trades

**Risk/Reward:**
- Minimum: 3:1 (enforced by Risk Manager veto)
- Target: 5-10% moves

**Earnings:**
- Exit before earnings unless part of thesis

### Conviction Tiers

| Bullish Votes | Conviction | Position Size |
|--------------|------------|---------------|
| 8-9/9 | High | 0.5-1% |
| 6-7/9 | Speculative | 0.25-0.5% |
| 5/9 | Watch/Neutral | 0% (add to watchlist) |
| <5/9 | Avoid | 0% |

### Veto Triggers (Non-negotiable)

**Risk Manager (Line-Item Veto):**
- R:R < 3:1
- Position size < 0.25%
- Portfolio correlation > 60%

**Macro Strategist (Contextual Veto):**
- SPY below MA-200 AND VIX > 30 → Long positions rejected
- Major event imminent (Fed, CPI) → New positions capped

---

## Position Trading Constraints (1m - 6m)

**Position Sizing:**
- High Conviction: 0.5-2%
- Medium Conviction: 0.5-1%

**Hold Period:**
- Target: 1-6 months
- Re-evaluate at major catalysts

**Stop-Loss:**
- Trailing stops or thesis-based exits
- Can hold through earnings if thesis supports

**Risk/Reward:**
- Minimum: 3:1
- Target: 10-25% moves

**Earnings:**
- Can hold through earnings if thesis supports

### Conviction Tiers

| Bullish Votes | Conviction | Position Size |
|--------------|------------|---------------|
| 5-6/6 | High | 0.5-2% |
| 4/6 | Medium | 0.5-1% |
| <4/6 | Avoid | 0% |

---

## Investment Model Constraints (1y+)

**Position Sizing:**
- High Conviction: 1-5%
- Medium Conviction: 1-3%
- Subject to correlation limits

**Hold Period:**
- Target: 1+ years
- Quarterly review cycle

**Exit Strategy:**
- Thesis-based exits, not technical stops
- Fundamental validation, not price volatility

### Conviction Tiers

| Bullish Votes | Conviction | Position Size |
|--------------|------------|---------------|
| 4/4 | High | 1-5% |
| 3/4 | Medium | 1-3% |
| <3/4 | Avoid | 0% |

---

## Veto Hierarchy (Non-negotiable)

### Priority 1: Risk Manager (Line-Item Veto)

**Triggers:**
- R:R below threshold (2:1 for day, 3:1 for swing)
- Position size below 0.25%
- Portfolio correlation > 60%

**Effect:** Trade is DEAD. Cannot be overridden.

### Priority 2: Macro Strategist (Contextual Veto)

**Triggers:**
- SPY below MA-200 AND VIX > 30 (bear market)
- Major macro event imminent (Fed decision, CPI print)

**Effect:** Long positions rejected OR conviction capped at Low.

### Priority 3: CIO (Cannot Override Vetoes)

The CIO must check for veto triggers BEFORE any synthesis or vote counting.

---

## Veto Check Process (MANDATORY - First Step)

```python
# Pseudo-code for veto check process
def check_vetoes(trade_params, portfolio):
    # Risk Manager Veto (Line-Item)
    if trade_params['rr_ratio'] < MIN_RR:
        return "AVOID - Risk Manager veto: R:R below minimum"
    if trade_params['position_size'] < MIN_POSITION:
        return "AVOID - Risk Manager veto: Position too small"
    if portfolio['correlation'] > MAX_CORRELATION:
        return "AVOID - Risk Manager veto: Correlation too high"

    # Macro Strategist Veto (Contextual)
    if market_regime == 'RISK_OFF':
        return "AVOID - Macro veto: Market in risk-off regime"

    # No veto triggered - proceed to analysis
    return None
```

---

## Correlation Limits

**Definition:** Correlation measures how closely the new position moves with existing positions.

| Correlation Level | Action |
|-------------------|--------|
| < 30% | No restriction |
| 30-60% | CIO considers concentration |
| > 60% | Risk Manager veto |

---

## Timeframe Parsing

**Input Format:** Unit suffixes indicate trading model

| Suffix | Unit | Model | Agents |
|--------|------|-------|--------|
| d | days | Scalping/Day Trading | 6 |
| w | weeks | Swing Trading | 10 |
| m | months | Position Trading | 7 |
| y | years | Investment | 5 |

**Examples:**
- `3d` → Scalping (3 days)
- `2w` → Swing (2 weeks)
- `6m` → Position (6 months)
- `2y` → Investment (2 years)

**Default:** If no timeframe specified, assume `4w` (Swing Trading)
