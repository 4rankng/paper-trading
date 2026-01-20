---
allowed-tools: Bash, Glob, Skill, Read
description: Multi-agent debate - trading analysis (ticker + timeframe) OR current affairs/macroeconomics (general topic)
argument-hint: [ticker] [timeframe] OR [general topic]
---

Execute multi-agent debate. Routes to appropriate skill based on input:

**1. Trading Debate (ticker + timeframe):**
- First argument is a stock ticker (e.g., NVDA, COIN, SPY)
- Second argument is timeframe

**Timeframe units:**
- `d` = days (e.g., `3d`, `7d`) → Scalping/Day trading (6-persona debate)
- `w` = weeks (e.g., `2w`, `4w`) → Swing trading (10-persona debate)
- `m` = months (e.g., `3m`, `6m`) → Position trading (7-persona debate)
- `y` = years (e.g., `1y`, `2y`) → Investment model (5-persona debate)

**Trading Examples:**
- `/debate COIN 3d` - 3 day scalping outlook
- `/debate COIN 4w` - 4 week swing trade outlook
- `/debate COIN 6m` - 6 month position trading outlook
- `/debate QQQ 1y` - 1 year investment outlook

**2. General Debate (topic only):**
- Single argument or phrase that's not a ticker
- Covers: geopolitics, economics, policy, markets

**General Examples:**
- `/debate Will US-EU trade war escalate?`
- `/debate Should the Fed cut rates in January?`
- `/debate Impact of AI on employment`
- `/debate Is a recession coming in 2026?`

## Routing Logic

**Step 1:** Detect input type
- If argument 1 is a ticker (1-5 letters, all caps) AND argument 2 exists with timeframe suffix → **Trading Debate**
- Otherwise → **General Debate**

**Step 2:** Execute appropriate skill
- Trading Debate: Execute `trading-debate` skill with ticker and timeframe
- General Debate: Execute `debate` skill with topic

## Output Format

The skill will produce a complete multi-agent debate output following its defined structure. **DO NOT add any additional summaries or recaps after the skill's conclusion.**

**The output ends at the skill's conclusion section.** Per output discipline rules:
- NO "Summary" sections
- NO "Key Takeaways" recaps
- NO repetition of verdict
- Clean termination after conclusion

## Constraints

**Trading Debate** (enforced by trading-debate skill):
- Scalping/Day Trading (1d-7d): Tight stops (1-1.5x ATR), max 0.5% position, min 2:1 R:R
- Swing Trading (1w-4w): Hard stop-loss (ATR-based), max 1% position, min 3:1 R:R
- Position Trading (1m-6m): Trailing stops, max 2% position, catalyst-driven exits
- Investment (1y+): Thesis-based exits, max 5% position, quarterly review
- Veto triggers: Risk Manager (R:R < minimum, correlation >60%), Macro Strategist (bear market conditions)

**General Debate** (enforced by debate skill):
- Confidence levels: High (80%+), Medium (60-80%), Low (40-60%), Research Needed (<40%)
- Source requirements: High credibility only (gov agencies, central banks, major news)
- Must include: Executive summary, scenarios, key indicators, sources
