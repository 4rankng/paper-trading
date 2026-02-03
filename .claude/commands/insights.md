---
name: insights
description: Provide LLM agent insights from existing analytics data. Use after running /analyze to get synthesized takeaways.
argument-hint: [TICKER]
disable-model-invocation: true
allowed-tools:
  - Glob
  - Read
---

Provide investment insights for [TICKER] based on existing analytics files.

## Prerequisites

First, verify analytics data exists for [TICKER]:

1. Use `Glob` to check for files in `analytics/[TICKER]/`
2. Return error if directory is empty or doesn't exist:
   ```
   Error: No analytics found for [TICKER].
   Run `/analyze [TICKER]` first to generate analysis files.
   ```

## Workflow

If analytics files exist, read all available analysis files:

1. **`analytics/[TICKER]/[TICKER]_technical_analysis.md`** - Price action, indicators, support/resistance
2. **`analytics/[TICKER]/[TICKER]_fundamental_analysis.md`** - Financials, business, competitive position
3. **`analytics/[TICKER]/[TICKER]_investment_thesis.md`** - Phenomenon, scenarios, catalysts

## Output Format

Provide concise insights in this structure:

```markdown
# [TICKER] Insights
**Price:** $X.XX | **Phenomenon:** [TYPE] | **Date:** [DATE]

---

## Executive Summary
[2-3 sentence overview of the investment case]

## Key Metrics
| Metric | Value | Assessment |
|--------|-------|------------|
| [Metric 1] | [Value] | [Bullish/Bearish/Neutral] |
| [Metric 2] | [Value] | [Bullish/Bearish/Neutral] |

## Strengths
- [Strength 1]
- [Strength 2]
- [Strength 3]

## Weaknesses
- [Weakness 1]
- [Weakness 2]
- [Weakness 3]

## Technical Setup
| Level | Price |
|-------|-------|
| Support | [levels] |
| Resistance | [levels] |

## Scenarios ([Timeframe])
| Scenario | Probability | Target | Return |
|----------|-------------|--------|--------|
| [Bull/Bear/Base] | X% | $X.XX | ±X% |

## Key Catalysts
| Date | Catalyst | Impact |
|------|----------|--------|
| [Date] | [Event] | High/Med/Low |

## Validation Metrics
**Green Flags:** [signals that validate thesis]
**Red Flags:** [signals that break thesis]

## Bottom Line
[2-3 sentence conclusion with actionable takeaway]
```

## Notes

- This command ONLY reads existing analytics - does not fetch new data
- For fresh analysis, use `/analyze [TICKER]`
- Keep insights concise and actionable
- Highlight the phenomenon classification prominently
