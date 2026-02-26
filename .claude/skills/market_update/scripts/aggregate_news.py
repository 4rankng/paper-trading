#!/usr/bin/env python3
"""
Aggregate latest news for holdings tickers.

This script gathers latest news from existing files (if fresh) or
fetches fresh headlines via WebSearch (if stale/missing).
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude"))

from shared.data_access import DataAccess, get_file_age_hours


def extract_headline_from_file(file_path: Path) -> Optional[str]:
    """
    Extract headline from news file.

    Args:
        file_path: Path to news markdown file

    Returns:
        Headline string or None
    """
    try:
        content = file_path.read_text()

        # Try to extract from YAML frontmatter
        yaml_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        if yaml_match:
            return yaml_match.group(1).strip()

        # Try to extract first heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        # Fallback to first non-empty line
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('---'):
                return line[:100]  # Truncate to 100 chars

        return None
    except Exception:
        return None


def check_news_freshness(ticker: str, max_age_hours: int = 24) -> bool:
    """
    Check if news files are fresh for a ticker.

    Args:
        ticker: Stock ticker symbol
        max_age_hours: Maximum age in hours to consider fresh

    Returns:
        True if fresh news exists, False otherwise
    """
    da = DataAccess()
    news_files = da.list_news_files(ticker, limit=1)

    if not news_files:
        return False

    # Check if latest file is fresh
    latest_file = news_files[0]
    return latest_file.age_hours < max_age_hours


def get_news_from_files(ticker: str, limit: int = 5) -> List[Dict]:
    """
    Get latest news from existing files.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of articles to return

    Returns:
        List of news article dicts with headline, source, date
    """
    da = DataAccess()
    news_files = da.list_news_files(ticker, limit=limit)

    articles = []
    for nf in news_files:
        headline = extract_headline_from_file(nf.path)
        if headline:
            # Try to extract source from YAML frontmatter
            try:
                content = nf.path.read_text()
                source_match = re.search(r'^source:\s*(.+)$', content, re.MULTILINE)
                source = source_match.group(1).strip() if source_match else "Unknown"
            except Exception:
                source = "Unknown"

            articles.append({
                "headline": headline,
                "source": source,
                "date": nf.date.strftime("%Y-%m-%d %H:%M") if nf.date else "Unknown",
                "age_hours": nf.age_hours,
                "path": str(nf.path)
            })

    return articles


def fetch_fresh_headlines(ticker: str, limit: int = 5) -> List[Dict]:
    """
    Fetch fresh headlines via WebSearch.

    NOTE: This is a placeholder. In the actual skill invocation,
    the LLM agent will use WebSearch tool to fetch fresh news.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of headlines

    Returns:
        Empty list (to be filled by LLM agent)
    """
    # This function is called from the script, but the actual
    # WebSearch will be done by the LLM agent when invoking the skill.
    # Return empty list to signal "no fresh news available locally"
    return []


def get_latest_news_for_tickers(tickers: List[str], limit: int = 5) -> Dict[str, List[Dict]]:
    """
    Get latest news for multiple tickers.

    Strategy:
    1. Check existing news files (freshness <24h)
    2. If stale/missing, signal need for WebSearch (empty list)

    Args:
        tickers: List of ticker symbols
        limit: Maximum number of articles per ticker

    Returns:
        Dict mapping ticker to list of news articles
    """
    results = {}

    for ticker in tickers:
        ticker_upper = ticker.upper()

        # Check if fresh news exists
        if check_news_freshness(ticker_upper):
            articles = get_news_from_files(ticker_upper, limit)
            results[ticker_upper] = articles
        else:
            # Signal need for fresh news
            results[ticker_upper] = []

    return results


def main():
    parser = argparse.ArgumentParser(description="Aggregate latest news for tickers")
    parser.add_argument("--tickers", type=str, required=True, help="Comma-separated list of tickers")
    parser.add_argument("--limit", type=int, default=5, help="Max articles per ticker")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]

    results = get_latest_news_for_tickers(tickers, args.limit)

    # Add freshness info
    output = {
        "news": results,
        "freshness": {
            ticker: check_news_freshness(ticker)
            for ticker in results.keys()
        }
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
