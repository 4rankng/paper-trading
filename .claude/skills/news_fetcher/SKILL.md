---
name: news-fetcher
description: Fetch and manage news articles from yfinance API or manual entry with YAML frontmatter. ALWAYS use for ANY news operations. **CRITICAL**: Before fetching news, ALWAYS run `list_news.py --ticker TICKER` first to check for existing articles and prevent duplicates. The yfinance API frequently returns the same articles multiple times. Triggers: "fetch news", "add news", "search news", "update article", "delete article", "news sentiment", "news by source", "news by date", "news keywords". Never manually create or edit news files - use this skill.
---

# News Fetcher Skill

Fetch and manage news articles with automatic slug generation and YAML frontmatter.

## Quick Start

```bash
# List existing articles (DO THIS FIRST BEFORE FETCHING)
python .claude/skills/news_fetcher/scripts/list_news.py --ticker NVDA

# Fetch from yfinance API (only after checking existing news)
python .claude/skills/news_fetcher/scripts/fetch_news.py --ticker NVDA --limit 20

# Add manual article
python .claude/skills/news_fetcher/scripts/add_news.py --ticker TCOM --title "Partnership" \
  --source "PR" --url "https://..." --content "..."

# Search articles
python .claude/skills/news_fetcher/scripts/search_news.py --query "partnership" --tickers TCOM,NVDA
```

**IMPORTANT**: Always run `list_news.py` before `fetch_news.py` to prevent duplicate articles.

## Common Workflows

### Daily News Fetch (DUPLICATE PREVENTION)
```bash
# STEP 1: Check existing news first (MANDATORY)
python .claude/skills/news_fetcher/scripts/list_news.py --ticker NVDA

# STEP 2: Review existing articles to avoid duplicates
# - Check titles, sources, URLs, and published dates
# - Skip fetch if recent articles already exist (same title/source within 2-3 days)

# STEP 3: Fetch only if needed
python .claude/skills/news_fetcher/scripts/fetch_news.py --ticker NVDA --limit 20
```

**IMPORTANT**: Always list existing news before fetching to prevent duplicates. The yfinance API may return the same articles multiple times across different fetch calls.

### Manual Article Entry
```bash
# Add press release or manual news
python .claude/skills/news_fetcher/scripts/add_news.py \
  --ticker TCOM \
  --title "Partnership Announced" \
  --source "Company PR" \
  --url "https://example.com" \
  --content "Full content..."
```

### Search and Analysis
```bash
# Find articles about specific topics
python .claude/skills/news_fetcher/scripts/search_news.py --query "earnings" --tickers TCOM,NVDA

# Filter by date range
python .claude/skills/news_fetcher/scripts/search_news.py --start 2026-01-01 --end 2026-01-15 \
  --tickers TCOM
```

### Batch Content Updates
```bash
# Fill in content for news files that only have weblinks
python .claude/skills/news_fetcher/scripts/update_news_content.py

# Fetch and update news content (batch processing)
python .claude/skills/news_fetcher/scripts/fetch_and_update_news.py

# Update all news articles with latest content
python .claude/skills/news_fetcher/scripts/update_all_news.py
```

## File Structure

**Location**: `news/{TICKER}/{YEAR}/{MONTH}/{SLUG}.md`

**Format**: Markdown with YAML frontmatter (title, source, published_date, url, tags)

## Advanced

**Complete scripts reference**: See [scripts.md](references/scripts.md) for all parameters and usage examples.
