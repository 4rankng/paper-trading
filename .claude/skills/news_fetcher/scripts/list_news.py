#!/usr/bin/env python3
"""
List all news articles for a ticker.

Usage:
    python list_news.py --ticker TCOM
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def list_ticker_news(ticker: str) -> dict:
    """
    List all news articles for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with list of news articles
    """
    project_root = get_project_root()
    news_dir = project_root / 'news'
    ticker = ticker.upper()

    ticker_news_dir = news_dir / ticker

    if not ticker_news_dir.exists():
        return {
            'status': 'success',
            'ticker': ticker,
            'count': 0,
            'articles': []
        }

    # Find all markdown files
    articles = []
    for md_file in sorted(ticker_news_dir.glob('**/*.md'), reverse=True):
        try:
            # Read file to extract frontmatter
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

            title = 'Unknown'
            source = 'Unknown'
            published_date = None
            url = ''

            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                # Extract fields from frontmatter
                title_match = re.search(r'title:\s*(.+)', frontmatter)
                source_match = re.search(r'source:\s*(.+)', frontmatter)
                date_match = re.search(r'published_date:\s*(.+)', frontmatter)
                url_match = re.search(r'url:\s*(.+)', frontmatter)

                if title_match:
                    title = title_match.group(1).strip()
                if source_match:
                    source = source_match.group(1).strip()
                if date_match:
                    published_date = date_match.group(1).strip()
                if url_match:
                    url = url_match.group(1).strip()

            articles.append({
                'slug': md_file.stem,
                'file': str(md_file.relative_to(project_root)),
                'title': title,
                'source': source,
                'published_date': published_date,
                'url': url
            })

        except Exception as e:
            # Skip files that can't be read
            continue

    return {
        'status': 'success',
        'ticker': ticker,
        'count': len(articles),
        'articles': articles
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='List all news articles for a ticker')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker symbol')

    args = parser.parse_args()

    result = list_ticker_news(args.ticker)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
