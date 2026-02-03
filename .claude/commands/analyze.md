---
name: analyze
description: Comprehensive stock analysis - orchestrates skills to create technical, fundamental, and thesis files with data-driven insights.
argument-hint: [ticker]
disable-model-invocation: true
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
  - Skill(analytics_generator)
  - Skill(portfolio_manager)
  - Skill(watchlist_manager)
  - Skill(news_fetcher)
---

Execute comprehensive analysis on [TICKER] by orchestrating skills.

## Workflow

Use `Skill` tool to invoke these skills in sequence:

1. **`analytics_generator`** skill - Main analysis driver
   - Fetches price data
   - Generates technical indicators
   - Aggregates 40+ signals into unified scores (NEW)
   - Creates 4 markdown files:
     - `analytics/[TICKER]/[TICKER]_trading_volume.md` (auto-generated technical scoring)
     - `analytics/[TICKER]/[TICKER]_technical_analysis.md`
     - `analytics/[TICKER]/[TICKER]_fundamental_analysis.md`
     - `analytics/[TICKER]/[TICKER]_investment_thesis.md`

2. **`portfolio_manager`** skill - Get holdings context
   - Check if [TICKER] is already a holding
   - Apply Inertia Principle if holding exists

3. **`watchlist_manager`** skill - Get Quick-Glance score
   - Retrieve existing score and factors
   - Add context to analysis

4. **`news_fetcher`** skill - Get recent news
   - Check existing articles (prevents duplicates)
   - Fetch recent articles if needed

## Output

After skill execution, output summary:

```markdown
## Analysis Complete: [TICKER]

**Files Created:**
- analytics/[TICKER]/[TICKER]_trading_volume.md (auto-generated scoring)
- analytics/[TICKER]/[TICKER]_technical_analysis.md
- analytics/[TICKER]/[TICKER]_fundamental_analysis.md
- analytics/[TICKER]/[TICKER]_investment_thesis.md

**Technical Health Score:** XX/100 - [Classification]
**Market Regime:** [Trending/Ranging/Volatile]
**Signal Convergence:** XX% ([High/Medium/Low] confidence)

**Context:**
- Portfolio: [Existing holding / New analysis]
- Watchlist Score: XX/100 (Rating: X)
- Recent News: X articles

**Key Insights:**
- [Phenomenon classification]
- [1-2 sentence thesis summary]
- [Primary catalyst]
```

## Notes

- Analytics files provide data-driven insights ONLY (no trading recommendations)
- For trading recommendations, use `/trade [TICKER]` command
- All file structure details are in `analytics_generator` skill
- Command only orchestrates, doesn't implement
