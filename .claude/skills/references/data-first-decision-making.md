# Data-First Decision Making

**CRITICAL: All recommendation skills MUST follow this workflow before ANY output.**

## The 3-Step Checklist

Before generating ANY trading plan, debate, position review, or watchlist update:

### 1. Read Existing Analytics Files
```
analytics/{TICKER}/{TICKER}_technical_analysis.md
analytics/{TICKER}/{TICKER}_fundamental_analysis.md
analytics/{TICKER}/{TICKER}_investment_thesis.md
```

### 2. Web Search for Fresh Data (Last 24-48h)
Use `WebSearch` tool for:
- `{TICKER} news today` - Latest headlines, breaking news
- `{TICKER} earnings guidance` - Recent guidance changes
- `{TICKER} analyst upgrade downgrade` - Street sentiment shifts
- `{TICKER} sector news` - Industry developments
- `{TICKER} insider trading` - Recent Form 4 activity

### 3. Check Market Sentiment
- CNN Fear & Greed Index: https://edition.cnn.com/markets/fear-and-greed

## Data Freshness Rules

| Condition | Action |
|-----------|--------|
| Analytics missing | Run `/analyze {TICKER}` |
| Analytics >24h old | Refresh with `/analyze {TICKER}` OR web search |
| Analytics <24h old | Proceed with web search for fresh context |

## Stale Data Warning

**Do NOT make recommendations based on stale analytics (>24 hours old) without web search for fresh data.**

Markets move fast. Yesterday's technical levels may not hold. Earnings guidance can change overnight. Analyst ratings shift daily.

---

**Used by:** `trading-plan`, `trading-debate`, `position-review`, `watchlist_manager`
