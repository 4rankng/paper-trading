# Output Format Reference

This document provides examples and guidelines for formatting market update output.

## Terminal Output Structure

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
  "headers": ["Ticker", "Price", "Change", "Value", "Thesis"],
  "rows": [
    ["LAES", "$3.52", "-2.5%", "$63,360", "VALID ✓"],
    ["WRD", "$7.70", "+1.8%", "$21,560", "WARNING ⚠"],
    ["PONY", "$13.35", "+0.5%", "$18,690", "VALID ✓"]
  ]
})

**Total Value:** $103,610 | **Cash:** $22.18 | **Total P/L:** -41.2%

---

### Latest News (Last 24h)

**LAES (VALID ✓):**
• LAES announces strategic partnership - 2h ago
• Q4 earnings beat expectations - 6h ago

**WRD (WARNING ⚠):**
• WRD expands into European market - 4h ago

**PONY (VALID ✓):**
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

## Visualization Format Examples

### viz:table for Holdings

```markdown
![viz:table]({
  "headers": ["Ticker", "Price", "Change", "Value", "Thesis"],
  "rows": [
    ["LAES", "$3.52", "-2.5%", "$63,360", "VALID ✓"],
    ["WRD", "$7.70", "+1.8%", "$21,560", "WARNING ⚠"]
  ]
})
```

**Key Points:**
- Use `![viz:table](...)` format
- Headers: Ticker, Price, Change, Value, Thesis
- Thesis status includes icon (✓, ⚠, ✗, ?)
- Prices formatted with $ prefix
- Change percentages with +/- prefix

### viz:chart for P/L Comparison

```markdown
![viz:chart]({
  "type":"chart",
  "chartType":"bar",
  "data":{
    "labels":["LAES","WRD","PONY"],
    "datasets":[{
      "label":"P/L %",
      "data":[-45.0,-30.0,-38.2],
      "backgroundColor":["#ef4444","#ef4444","#ef4444"]
    }]
  }
})
```

**Key Points:**
- Use `![viz:chart](...)` format with `type: "chart"` and `chartType: "bar"`
- For negative P/L: red (#ef4444)
- For positive P/L: green (#22c55e)
- For neutral: yellow (#fef08a)

### Mobile-Friendly Compact Format

For mobile terminals, use compact lists instead of wide tables:

```
**LAES** - $3.52 (-2.5%) - VALID ✓
Strong earnings beat and partnership.

**WRD** - $7.70 (+1.8%) - WARNING ⚠
Technical breakdown, monitor closely.

**PONY** - $13.35 (+0.5%) - VALID ✓
Funding validates business model.
```

## Thesis Status Icons

| Status | Icon | Meaning |
|--------|------|---------|
| VALID | ✓ | Thesis intact, fundamentals strong |
| WARNING | ⚠ | Monitor closely, potential issues |
| DEAD | ✗ | Thesis invalidated, consider exit |
| UNKNOWN | ? | Insufficient data for assessment |

## Color Coding for P/L

| Value Range | Color | Hex |
|-------------|-------|-----|
| > 0% | Green | #22c55e |
| 0% | Yellow | #fef08a |
| < 0% | Red | #ef4444 |

## Data Freshness Indicators

| Data Type | Fresh | Stale | Missing |
|-----------|-------|-------|---------|
| Prices | ✓ Current (<1h) | ⚠ Stale (>24h) | ✗ N/A |
| News | ✓ Current (<24h) | ⚠ Stale (>24h) | ✗ N/A |
| Thesis | ✓ Reassessed | N/A | ⚠ No thesis |
| Macro | ✓ Current (<7d) | ⚠ Old (>7d) | ✗ N/A |
| Fear & Greed | ✓ Current (<1h) | ⚠ N/A | ✗ N/A |

## Error Messages

### No Holdings

```
## Market Update: CORE Portfolio

**No holdings found in CORE portfolio.**

Consider adding positions or check a different portfolio.
Available portfolios: CORE, LLM_HELP
```

### Portfolio Not Found

```
## Error

**Portfolio 'XXX' not found.**

Available portfolios: CORE, LLM_HELP

Use --portfolio flag to specify a valid portfolio name.
```

### Partial Data (Error Resilience)

```
### Data Freshness
✓ Prices: Current (from yfinance, <5min old)
⚠ News: Stale (>24h old, using cached data)
✓ Thesis: Reassessed with LLM using available data
✓ Macro: Current (thesis updated 2026-02-03)
⚠ Fear & Greed: N/A (connection failed)

**Note:** Some data may be outdated. Use --force-refresh to update.
```
