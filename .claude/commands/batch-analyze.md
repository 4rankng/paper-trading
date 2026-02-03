---
name: batch-analyze
description: Run analysis in parallel mode for multiple tickers. Use when analyzing 3+ stocks simultaneously for efficiency.
argument-hint: [segment] [--parallel]
disable-model-invocation: true
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
  - Skill(analyze)
  - Skill(analytics_generator)
  - Skill(watchlist_manager)
---

# Batch Analyze

You are orchestrating batch analysis for multiple tickers. Use the batch_analyze skill to:

1. **Parse the segment argument**:
   - `all` - All watchlist tickers
   - `core` - Compounder-type holdings
   - `moonshots` - Moonshot-type holdings
   - Comma-separated tickers (e.g., `NVDA,AAPL,MSFT`)

2. **Load tickers from watchlist** based on segment

3. **For each ticker** (in parallel if --parallel flag):
   - Check if analytics files exist and are fresh (<24h)
   - If missing or stale: fetch prices, generate technical/fundamental/thesis
   - Calculate quality scores
   - Classify investment type if needed

4. **Output summary**:
   - Total tickers processed
   - Analytics created/updated
   - Quality scores
   - Any errors or warnings

Use the analytics_generator and watchlist_manager skills for the actual analysis work.
