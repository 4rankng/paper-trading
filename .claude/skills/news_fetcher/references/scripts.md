# News Fetcher Scripts Reference

Complete documentation for all news management scripts.

## fetch_news.py

Fetch news from yfinance API with retry logic and automatic slug generation.

### Usage

```bash
python scripts/fetch_news.py --ticker NVDA --limit 20
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--limit`: Maximum number of articles to fetch (default: 20)
- `--days`: Number of days to look back (default: 30)

### Behavior

- Fetches from yfinance news API
- Generates URL-safe slugs from article titles
- Creates directory structure: `news/{TICKER}/{YEAR}/{MONTH}/`
- Retries failed requests with exponential backoff
- Skips duplicates based on URL matching

## add_news.py

Manually add a news article with auto-generated slug.

### Usage

```bash
python scripts/add_news.py \
  --ticker TCOM \
  --title "Partnership Announced" \
  --source "Press Release" \
  --url "https://example.com/article" \
  --content "Full article content..."
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--title`: Article headline (required)
- `--source`: Source name (e.g., "Bloomberg", "Reuters") (required)
- `--url`: Article URL (required)
- `--content`: Article body content (required)
- `--published-date`: Publication date (YYYY-MM-DD) (optional, defaults to today)
- `--tags`: Comma-separated tags (optional)

### Behavior

- Auto-generates URL-safe slug from title
- Creates directory structure if needed
- Validates required fields
- Preserves YAML frontmatter format

## update_news.py

Update article content while preserving YAML frontmatter.

### Usage

```bash
python scripts/update_news.py \
  --file news/TCOM/2026/01/partnership-announced.md \
  --content "Updated content..."
```

### Parameters

- `--file`: Path to article file (required)
- `--content`: New content for article body (required)

### Behavior

- Preserves existing YAML frontmatter
- Only updates article body content
- Validates file exists before updating

## delete_news.py

Delete article file with confirmation.

### Usage

```bash
python scripts/delete_news.py --file news/TCOM/2026/01/partnership-announced.md
```

### Parameters

- `--file`: Path to article file (required)
- `--force`: Skip confirmation prompt (optional)

### Behavior

- Prompts for confirmation unless `--force` flag used
- Validates file exists before deletion

## list_news.py

List all articles for a ticker with metadata.

### Usage

```bash
# List all articles for ticker
python scripts/list_news.py --ticker TCOM

# Output as JSON
python scripts/list_news.py --ticker TCOM --format json
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--format`: Output format (human or json) (default: human)
- `--limit`: Maximum number of articles to show (optional)

## search_news.py

Search by query, source, date range, or tags across tickers.

### Usage

```bash
# Search by keyword
python scripts/search_news.py --query "partnership" --tickers TCOM,NVDA

# Search by source
python scripts/search_news.py --source "Reuters" --tickers TCOM

# Search by date range
python scripts/search_news.py --start 2026-01-01 --end 2026-01-15 --tickers TCOM

# Search by tags
python scripts/search_news.py --tags "earnings,catalyst" --tickers TCOM
```

### Parameters

- `--query`: Keyword search in title and content
- `--tickers`: Comma-separated ticker symbols (required)
- `--source`: Filter by source name
- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD)
- `--tags`: Comma-separated tags
- `--format`: Output format (human or json) (default: human)

### Behavior

- Searches title and content for query matches
- Combines multiple filters with AND logic
- Returns articles matching all specified criteria

## File Structure

**Location**: `news/{TICKER}/{YEAR}/{MONTH}/{SLUG}.md`

**Format**: Markdown with YAML frontmatter

```yaml
---
title: "Article Title"
source: "Source Name"
published_date: "YYYY-MM-DD"
url: "https://example.com/article"
tags: ["tag1", "tag2"]
---

Article body content here.
```
