# Data Gap Detection Workflow

Identify and resolve missing information before launching multi-agent debates.

---

## Overview

Before running any trading debate, ensure all required data is available. Missing or stale data leads to poor analysis and wasted compute.

## Priority Data Gaps

### Critical (Must Fix Before Debate)

| Gap | Impact | Detection | Resolution |
|-----|--------|-----------|------------|
| Missing analytics files | Cannot evaluate | validate_analytics.py script | Run `/analyze [TICKER]` |
| Stale analytics (>24h) | Outdated signals | File modification time | Run `/analyze [TICKER]` |
| Missing investment thesis | No thesis context | thesis.md missing | Run `/analyze [TICKER]` |
| Missing machine type | Wrong personas | thesis.md incomplete | Run `/ask [TICKER]` |

### Important (Check Before Debate)

| Gap | Impact | Detection | Resolution |
|-----|--------|-----------|------------|
| Missing sector context | Limited macro view | fundamental_analysis.md | Add sector to thesis |
| Missing catalysts | No event-driven setup | thesis.md empty catalysts | Run `/ask [TICKER]` |
| Stale news (>7 days) | Missed recent events | news/ folder timestamp | Run `news_fetcher` skill |

### Nice to Have

| Gap | Impact | Detection | Resolution |
|-----|--------|-----------|------------|
| Missing price targets | No reference levels | technical_analysis.md | Manual analysis |
| Missing analyst ratings | No sentiment context | fundamental_analysis.md | Optional |

---

## Detection Process

### Step 1: Run Validation Script

```bash
python .claude/skills/trading-debate/scripts/validate_analytics.py TICKER
```

**Expected output if valid:**
```
✓ Analytics files validated for TICKER
  TICKER_technical_analysis.md: 2.3h old
  TICKER_fundamental_analysis.md: 2.3h old
  TICKER_investment_thesis.md: 2.3h old
```

**Expected output if invalid:**
```
✗ Validation failed for TICKER
  ERROR: Missing: analytics/TICKER/TICKER_technical_analysis.md
  WARNING: Stale: TICKER_fundamental_analysis.md is 48.5h old (max 24h)
```

### Step 2: Check for Data Gaps Using Ask Skill

If validation passes but you need more context, run:

```bash
/ask TICKER
```

This generates 5 factual questions about the ticker to fill gaps in:
- Machine type (Hyper-growth, Compounder, Deep Value, etc.)
- Sector classification
- Business model understanding
- Competitive landscape
- Key catalysts

### Step 3: Check News Freshness

```bash
# List news articles with timestamps
ls -lh news/TICKER/
```

If news is missing or stale (>7 days), fetch fresh articles using the `news_fetcher` skill.

---

## Resolution Commands

| Problem | Command |
|---------|---------|
| Missing or stale analytics | `/analyze TICKER` |
| Missing thesis context | `/ask TICKER` |
| Missing recent news | Use `news_fetcher` skill |
| Missing price data | Use `analytics_generator` skill |

---

## Gap Impact on Debate Quality

### High Confidence Debate Requirements

For a high-quality debate, the following must be present:

1. **Fresh analytics (<24h)** - Technicals, fundamentals, thesis
2. **Machine type** - Drives persona selection and bias
3. **Sector context** - Macro strategist needs this
4. **Recent news (<7 days)** - Sentiment analysis
5. **Catalyst timeline** - Event-driven setup validation

### What Happens If Gaps Remain

| Gap | Effect |
|-----|--------|
| Stale analytics | Technical signals may be invalid |
| Missing machine type | Personas use generic defaults |
| Missing sector | Macro analysis will be weak |
| Stale news | Sentiment reading may be outdated |

### Downgrading Conviction

If critical gaps cannot be resolved:

1. **Document the gap** explicitly in the debate
2. **Cap conviction at Low** regardless of vote count
3. **Consider deferring** the debate until data is available

---

## Integration with Trading Debate

### Before Running `/debate TICKER TIMEFRAME`

```bash
# 1. Validate analytics
python .claude/skills/trading-debate/scripts/validate_analytics.py TICKER

# 2. If validation fails, refresh
/analyze TICKER

# 3. Check for additional gaps
/ask TICKER

# 4. Now run debate
/debate TICKER TIMEFRAME
```

### Example Workflow

```bash
# User wants swing trade analysis for NVDA
/debate NVDA 2w

# Skill auto-checks:
# - Analytics fresh? → If no, run /analyze NVDA
# - Thesis complete? → If no, run /ask NVDA
# - News fresh? → If no, fetch news

# Then proceed with debate
```

---

## Troubleshooting

### "Analytics files missing"

**Cause:** Required files don't exist in `analytics/[TICKER]/`

**Solution:** Run `/analyze [TICKER]` to generate all three files.

### "Analytics stale but /analyze already run"

**Cause:** Market moved significantly since last analysis

**Solution:** Run analytics_generator skill directly to force refresh.

### "Thesis incomplete - missing machine type"

**Cause:** Investment thesis doesn't specify machine classification

**Solution:** Run `/ask [TICKER]` to generate questions, then update thesis manually.

### "No recent news articles"

**Cause:** News folder empty or articles >7 days old

**Solution:** Use `news_fetcher` skill to fetch latest articles.
