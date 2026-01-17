# Exit Logic by Machine Type

## HYPE_MACHINE Exit Rules

**Primary Triggers:**
- Price closes below technical support level → SELL/TRIM
- Momentum score drops significantly (e.g., RSI breaks below 40) → SELL/TRIM
- Volume dry-up (no buyers at current levels) → SELL/TRIM

**Technical Support Levels:**
- MA20 (short-term positions)
- MA50 (medium-term positions)
- Key consolidation lows
- Previous breakout levels

**Stop Loss:** -5% from entry or support break (whichever comes first)

**Take Profit:** Scale out on 20%+ gains

**Otherwise:** HOLD

---

## EARNINGS_MACHINE Exit Rules

**Primary Triggers:**
- Fundamental Score drops below 50 → SELL
- Thesis invalidated (specific catalyst fails) → SELL
- Business model broken → SELL

**What NOT to Sell For:**
- ❌ Price drop
- ❌ Sentiment weakness
- ❌ Technical breakdown
- ❌ Volatility
- ❌ Position size too large/small
- ❌ Underperformance vs benchmarks

**Stop Loss:** Fundamental degradation only

**Take Profit:** Intrinsic value convergence (3+ year horizon)

**Otherwise:** HOLD (or add if price drops on fear)

---

## MEAN_REVERSION_MACHINE Exit Rules

**Primary Triggers:**
- Fundamental Score drops below 50 → SELL
- Sentiment reverses to positive (>60) without price follow-through → TRIM/SELL
- Graham gap closes (normalization) → Take profits

**Dual Stop Conditions:**
1. Fundamental degradation (see EARNINGS_MACHINE)
2. Sentiment reversal without price movement

**Take Profit:** When sentiment normalizes and price converges to fundamentals

**Otherwise:** HOLD through volatility
