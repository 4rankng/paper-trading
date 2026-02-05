# Visualization Output Guide

**CRITICAL:** When outputting data in responses, NEVER use markdown tables. Use the visualization format below.

## Forbidden Formats (NEVER USE)

❌ **MARKDOWN TABLES** (will NOT render properly in webapp):
```markdown
| Ticker | Shares | Value |
|--------|--------|-------|
| AAPL   | 100    | $5K   |
```

❌ **ASCII/TERMINAL ART:**
```
+-------+--------+
| Ticker | Shares |
+-------+--------+
```

❌ **BOX DRAWING:**
```
┌───────┬────────┐
│ Issue │ Status │
└───────┴────────┘
```

## Required Visualization Format

### For Tabular Data (holdings, trade history, comparisons)

**USE viz:table:**
```
![viz:table]({"headers":["Ticker","Shares","Value","P/L %"],"rows":[["AAPL",100,"$50,000","+12.5%"],["MSFT",50,"$30,000","+8.3%"]]})
```

### For Price Trends Over Time (time-series data)

**USE viz:chart with chartType="line":**
```
![viz:chart]({"type":"chart","chartType":"line","data":{"labels":["Jan","Feb","Mar"],"datasets":[{"label":"Portfolio Value","data":[100000,105000,102000]}]},"options":{"plugins":{"title":{"display":true,"text":"Portfolio Value Trend"}}}})
```

### For Comparisons (holdings by value, P/L by ticker)

**USE viz:chart with chartType="bar":**
```
![viz:chart]({"type":"chart","chartType":"bar","data":{"labels":["AAPL","MSFT","GOOGL"],"datasets":[{"label":"Holdings Value","data":[50000,30000,20000]}]},"options":{"plugins":{"title":{"display":true,"text":"Holdings by Stock"}}}})
```

### For Distributions (portfolio allocation, sector breakdown)

**USE viz:pie:**
```
![viz:pie]({"data":[{"label":"CORE","value":127522},{"label":"AI_PICKS","value":13749}],"options":{"title":"Portfolio Allocation"}})
```

## Critical Syntax Rules

- Line/Bar charts: `type="chart"` with `chartType="line"` or `chartType="bar"` inside
- Pie charts: `type="pie"`
- Tables: `type="table"`
- NEVER use `type="line"` or `type="bar"` directly - this will fail to render!

## When to Use Each Visualization

| Data Type | Use This |
|-----------|----------|
| Time-series (price history, portfolio growth) | **LINE CHART** |
| Comparisons (holdings, P/L by ticker) | **BAR CHART** |
| Parts-of-whole (allocation, sectors) | **PIE CHART** |
| Detailed listings (holdings list, trade history) | **TABLE** |
