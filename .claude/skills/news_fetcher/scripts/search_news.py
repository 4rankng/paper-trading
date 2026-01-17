#!/usr/bin/env python3
"""
Search news by multiple criteria across tickers.

Usage:
    python search_news.py --query "partnership" --tickers TCOM,NVDA
    python search_news.py --source "TechNews" --limit 10
    python search_news.py --start-date 2026-01-01 --end-date 2026-01-15
    python search_news.py --tags "ai,semiconductors"
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def search_news(
    query: Optional[str] = None,
    tickers: Optional[List[str]] = None,
    source: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> dict:
    """
    Search news by multiple criteria across tickers.

    Args:
        query: Search query keyword (case-insensitive)
        tickers: List of tickers to search (default: all)
        source: Filter by source/publisher
        start_date: Filter articles after this date (YYYY-MM-DD)
        end_date: Filter articles before this date (YYYY-MM-DD)
        tags: List of tags to filter by
        limit: Maximum number of results to return

    Returns:
        Dictionary with matching articles
    """
    project_root = get_project_root()
    news_dir = project_root / 'news'

    # Normalize query
    query_lower = query.lower() if query else None

    # Parse dates
    start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

    # Normalize source
    source_lower = source.lower() if source else None

    # Normalize tags
    tags_lower = [t.lower() for t in tags] if tags else None

    # Determine which tickers to search
    if tickers:
        ticker_dirs = [news_dir / t.upper() for t in tickers]
    else:
        # Search all tickers
        ticker_dirs = [d for d in news_dir.iterdir() if d.is_dir()]

    matches = []

    for ticker_dir in ticker_dirs:
        if not ticker_dir.exists():
            continue

        ticker = ticker_dir.name

        # Find all markdown files
        for md_file in ticker_dir.glob('**/*.md'):
            try:
                # Read file
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract frontmatter
                frontmatter = {}
                frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                if frontmatter_match:
                    for line in frontmatter_match.group(1).split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip()

                # Extract title
                title = frontmatter.get('title', 'Unknown')

                # Extract source
                article_source = frontmatter.get('source', 'Unknown')

                # Extract published date
                pub_date_str = frontmatter.get('published_date', '')
                pub_date = None
                if pub_date_str:
                    try:
                        pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass

                # Extract tags
                article_tags = []
                tags_str = frontmatter.get('tags', '')
                if tags_str:
                    # Tags can be comma-separated or in array format
                    article_tags = [t.strip().lower() for t in tags_str.replace('[', '').replace(']', '').replace('"', '').split(',')]

                # Apply filters
                # 1. Query filter
                if query_lower and query_lower not in content.lower():
                    continue

                # 2. Source filter
                if source_lower and source_lower not in article_source.lower():
                    continue

                # 3. Date range filter
                if pub_date:
                    if start_dt and pub_date < start_dt:
                        continue
                    if end_dt and pub_date > end_dt:
                        continue

                # 4. Tags filter
                if tags_lower:
                    if not any(tag in article_tags for tag in tags_lower):
                        continue

                # Extract slug
                slug = md_file.stem

                # Find context around match if query provided
                context_lines = []
                if query_lower:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            # Get context (2 lines before and after)
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])
                            context_lines.append(context)

                match_data = {
                    'ticker': ticker,
                    'slug': slug,
                    'file': str(md_file.relative_to(project_root)),
                    'title': title,
                    'source': article_source,
                    'published_date': pub_date_str,
                }

                if context_lines:
                    match_data['context'] = context_lines[:3]  # Limit to 3 contexts

                if article_tags:
                    match_data['tags'] = frontmatter.get('tags', '')

                matches.append(match_data)

            except Exception:
                # Skip files that can't be read
                continue

    # Sort by date (newest first) if dates available
    matches_with_dates = [m for m in matches if m.get('published_date')]
    matches_without_dates = [m for m in matches if not m.get('published_date')]
    matches_with_dates.sort(key=lambda x: x['published_date'], reverse=True)
    matches = matches_with_dates + matches_without_dates

    # Apply limit
    if limit and limit > 0:
        matches = matches[:limit]

    return {
        'status': 'success',
        'query': query or '',
        'filters': {
            'tickers': tickers or ['all'],
            'source': source or 'any',
            'start_date': start_date or 'any',
            'end_date': end_date or 'any',
            'tags': tags or ['any'],
            'limit': limit or 'none'
        },
        'count': len(matches),
        'matches': matches
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Search news by multiple criteria')
    parser.add_argument('--query', type=str, help='Search query keyword')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers (default: all)')
    parser.add_argument('--source', type=str, help='Filter by source/publisher')
    parser.add_argument('--start-date', type=str, help='Filter articles after this date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Filter articles before this date (YYYY-MM-DD)')
    parser.add_argument('--tags', type=str, help='Comma-separated list of tags to filter by')
    parser.add_argument('--limit', type=int, help='Maximum number of results to return')

    args = parser.parse_args()

    # At least one filter must be specified
    if not any([args.query, args.source, args.start_date, args.end_date, args.tags]):
        parser.error('At least one filter must be specified (--query, --source, --start-date, --end-date, or --tags)')

    tickers = args.tickers.split(',') if args.tickers else None
    tags = args.tags.split(',') if args.tags else None

    result = search_news(
        query=args.query,
        tickers=tickers,
        source=args.source,
        start_date=args.start_date,
        end_date=args.end_date,
        tags=tags,
        limit=args.limit
    )
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
