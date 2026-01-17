#!/usr/bin/env python3
"""
Manually add a news article.

Usage:
    python add_news.py --ticker TCOM --title "..." --source "..." --url "..." --content "..."
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from news headline."""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-').lower()
    return slug[:100]


def add_news_article(ticker: str, title: str, source: str, url: str, content: str, published_date: str = None) -> dict:
    """
    Add a manual news article.

    Args:
        ticker: Stock ticker symbol
        title: Article title
        source: Article source
        url: Article URL
        content: Article content
        published_date: Optional published date (format: YYYY-MM-DD HH:MM:SS)

    Returns:
        Dictionary with result
    """
    project_root = get_project_root()
    news_dir = project_root / 'news'
    ticker = ticker.upper()

    # Generate slug
    slug = generate_slug(title)

    # Parse published date or use current date
    if published_date:
        try:
            pub_date = datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pub_date = datetime.now()
    else:
        pub_date = datetime.now()

    pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M:%S')
    year = pub_date.strftime('%Y')
    month = pub_date.strftime('%m')

    # Create directory structure
    ticker_news_dir = news_dir / ticker / year / month
    ticker_news_dir.mkdir(parents=True, exist_ok=True)

    filepath = ticker_news_dir / f"{slug}.md"

    # Handle duplicate slugs
    counter = 1
    while filepath.exists():
        filepath = ticker_news_dir / f"{slug}-{counter}.md"
        counter += 1

    # Write markdown with frontmatter
    markdown_content = f"""---
title: {title}
source: {source}
published_date: {pub_date_str}
url: {url}
---

# {title}

**Source**: {source}
**Published**: {pub_date_str}
**Link**: {url}

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return {
        'status': 'success',
        'ticker': ticker,
        'file': str(filepath.relative_to(project_root)),
        'slug': filepath.stem,
        'title': title
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Add a manual news article')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker symbol')
    parser.add_argument('--title', required=True, type=str, help='Article title')
    parser.add_argument('--source', required=True, type=str, help='Article source')
    parser.add_argument('--url', required=True, type=str, help='Article URL')
    parser.add_argument('--content', required=True, type=str, help='Article content')
    parser.add_argument('--published-date', type=str, help='Published date (format: YYYY-MM-DD HH:MM:SS)')

    args = parser.parse_args()

    result = add_news_article(args.ticker, args.title, args.source, args.url, args.content, args.published_date)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
