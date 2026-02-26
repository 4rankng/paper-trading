---
name: market-update
description: Generate at-a-glance market update for current holdings including latest news, prices, LLM-based thesis reassessment, and macro context. Use for: "market update", "portfolio update", "what's happening with my stocks", "update on holdings", "check my positions". Supports multi-portfolio: specify --portfolio to target specific portfolio.
allowed-tools:
  - Read
  - Bash(python:*)
  - WebSearch
  - mcp__web-reader__webReader
  - mcp__web-search-prime__webSearchPrime
  - Skill
user-invocable: true
context: main
agent: general-purpose
---

# Market Update Skill

Generate at-a-glance market update for current holdings with fresh data and LLM-based thesis reassessment.

## Quick Start

```bash
# Get market update for default portfolio
/market-update

# Get market update for specific portfolio
/market-update --portfolio CORE

# Force refresh all data (ignore cache)
/market-update --force-refresh
```

## Output Format

**CRITICAL: NEVER use markdown tables in responses.** Use viz:table and viz:chart format per [visualization guide](../references/visualization-guide.md).

### Example Output Structure

```
## Market Update: CORE Portfolio
**Generated:** 2026-02-07 14:30:00

### Market Context
**Fear & Greed:** 45 Neutral (→ No change)
**Macro Stance:** RISK-ON | Risk: MEDIUM
*Summary: Moderate growth with policy uncertainty.*

---

### Holdings Summary (3 positions)

![viz:table]({
  "headers": ["Ticker", "Price", "Change", "Value", "P/L %", "Thesis"],
  "rows": [
    ["LAES", "$3.52", "-2.5%", "$63,360", "-45.0%", "VALID ✓"],
    ["WRD", "$7.70", "+1.8%", "$21,560", "-30.0%", "WARNING ⚠"],
    ["PONY", "$13.35", "+0.5%", "$18,690", "-38.2%", "VALID ✓"]
  ]
})

**Total Value:** $103,610 | **Cash:** $22.18 | **Total P/L:** -41.2%

---

### Latest News (Last 24h)

**LAES (VALID - Fundamentals intact):**
• LAES announces strategic partnership - 2h ago
• Q4 earnings beat expectations - 6h ago

**WRD (WARNING - Technical breakdown):**
• WRD expands into European market - 4h ago

**PONY (VALID - On track):**
• PONY secures $50M funding round - 3h ago

---

### Thesis Reassessment (LLM Analysis)

| Ticker | Status | Rationale | Confidence |
|--------|--------|-----------|------------|
| LAES | VALID ✓ | Strong earnings beat and new partnership validate growth thesis. | HIGH |
| WRD | WARNING ⚠ | Expansion news positive, but technical breakdown suggests momentum shift. | MEDIUM |
| PONY | VALID ✓ | Funding round validates business model. | HIGH |

---

### Data Freshness
✓ Prices: Current (from yfinance, <5min old)
✓ News: Current (fetched fresh via WebSearch)
✓ Thesis: Reassessed with LLM using fresh data
✓ Macro: Current (thesis updated 2026-02-03)
```

## Data Freshness Strategy

| Data Type | Fresh | Stale | Action When Stale |
|-----------|-------|-------|-------------------|
| Prices | <1h old | >24h old | Fetch from yfinance |
| News | <24h old | >24h old | WebSearch for fresh headlines |
| Thesis | N/A | N/A | Always reassess with LLM using fresh news |
| Macro Thesis | <7 days old | >7 days old | Warning only |
| Fear & Greed | <1h old | >1h old | Show staleness warning |

## Error Handling

| Error Scenario | Response |
|----------------|----------|
| No holdings in portfolio | "No holdings found in CORE portfolio." |
| Portfolio not found | "Portfolio 'XXX' not found. Available: CORE, LLM_HELP" |
| Price CSV missing/stale | Fetch from yfinance with warning |
| yfinance timeout | Fallback to CSV with staleness warning |
| No news files | Use WebSearch for fresh headlines |
| News files stale | Fetch fresh via WebSearch |
| WebSearch failed | Return empty news list with warning |
| Analytics files missing | Set status="UNKNOWN" in reassessment |
| Fear & Greed unreachable | Show "N/A" for Fear & Greed |
| No macro thesis | Warning: "No macro analysis available" |
| LLM reassessment fails | Set status="UNKNOWN", confidence="LOW" |

## Workflow

### Step 1: Get Holdings Summary
- Read portfolio from `portfolios.json` using `DataAccess.get_portfolio()`
- Calculate market_value, gain_loss, gain_loss_pct for each holding
- Return structured dict with portfolio summary

### Step 2: Fetch Current Prices
- Get current prices for all holdings tickers
- Strategy: CSV (if fresh) → yfinance (if stale/missing)
- Return prices with change %

### Step 3: Aggregate Latest News
- Gather latest news for holdings tickers
- Check existing news files (freshness <24h)
- Fetch fresh news via WebSearch if stale/missing
- Return top 5 headlines per ticker

### Step 4: Check Macro Context
- Fetch CNN Fear & Greed Index via webReader
- Read latest macro thesis from `macro/theses/`
- Return stance, risk_level, summary

### Step 5: LLM Thesis Reassessment
- For each ticker, run LLM-based reassessment
- Inputs: existing thesis (if any), latest news, price action
- Output: status (VALID/DEAD/WARNING/UNKNOWN), rationale, confidence
- **Does NOT update thesis files automatically**

### Step 6: Generate Output
- Format with viz:table for holdings
- Include macro summary at top
- Add latest news and thesis reassessment
- Include data freshness warnings at bottom

## Key Design Decisions

1. **LLM Thesis Reassessment:** Uses LLM to analyze fresh news + price action and determine thesis status (VALID/DEAD/WARNING). Does NOT update thesis files automatically - only reports status.

2. **Data Freshness First:** Always checks file timestamps, fetches fresh data via WebSearch/yfinance if files are stale.

3. **Visualization Format:** Uses viz:table and viz:chart format (not markdown tables) per project standards.

4. **Error Resilience:** Continues with partial data if some components fail (e.g., no news → show empty news section with warning).

5. **Multi-Portfolio Support:** Default uses `metadata.default_portfolio`, can specify with `--portfolio` flag.

6. **Inertia Principle Applied:** LLM reassessment defaults to VALID unless strong evidence of DEAD thesis.

## References

- [Visualization Guide](../references/visualization-guide.md) - Output format standards
- [position-review](../position-review/SKILL.md) - Thesis validation patterns
- [macro_fetcher](../macro_fetcher/SKILL.md) - Macro context patterns
- [news_fetcher](../news_fetcher/SKILL.md) - News fetching patterns
