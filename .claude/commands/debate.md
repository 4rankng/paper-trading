---
allowed-tools: Bash, Glob, Skill, Read
description: Multi-agent trading debate with adaptive models (scalping, swing, position, investment)
argument-hint: [ticker] [timeframe]
---

Execute multi-agent trading debate on [TICKER] with [TIMEFRAME] analysis horizon.

**Timeframe units:**
- `d` = days (e.g., `3d`, `7d`) → Scalping/Day trading (6-persona debate)
- `w` = weeks (e.g., `2w`, `4w`) → Swing trading (10-persona debate)
- `m` = months (e.g., `3m`, `6m`) → Position trading (7-persona debate)
- `y` = years (e.g., `1y`, `2y`) → Investment model (5-persona debate)

**Examples:**
- `/debate COIN 3d` - 3 day scalping outlook
- `/debate COIN 4w` - 4 week swing trade outlook
- `/debate COIN 6m` - 6 month position trading outlook
- `/debate QQQ 1y` - 1 year investment outlook

Execute the trading-debate skill with the ticker and timeframe parameters.

## Output Format

The skill will produce a complete multi-agent debate output following its defined structure. **DO NOT add any additional summaries or recaps after the skill's conclusion.**

**The output ends at the skill's "Conclusion" section.** Per output discipline rules:
- NO "Summary" sections
- NO "Key Takeaways" recaps
- NO repetition of verdict
- Clean termination after conclusion

## Constraints

All constraints are enforced by the trading-debate skill:
- **Scalping/Day Trading (1d-7d)**: Tight stops (1-1.5x ATR), max 0.5% position, min 2:1 R:R
- **Swing Trading (1w-4w)**: Hard stop-loss (ATR-based), max 1% position, min 3:1 R:R
- **Position Trading (1m-6m)**: Trailing stops, max 2% position, catalyst-driven exits
- **Investment (1y+)**: Thesis-based exits, max 5% position, quarterly review

Veto triggers enforced by skill personas:
- Risk Manager: R:R < model minimum, position <0.25%, correlation >60%
- Macro Strategist: SPY below MA-200 + VIX >30 (bear market)
