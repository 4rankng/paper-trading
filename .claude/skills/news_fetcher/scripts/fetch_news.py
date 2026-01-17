#!/usr/bin/env python3
"""
Fetch news for stocks and save as individual markdown files.

This script fetches news headlines from yfinance and saves them as
individual markdown files organized by ticker, year, and month.

Usage:
    python fetch_news.py --ticker NVDA --limit 20
    python fetch_news.py --tickers NVDA,AAPL,MSFT

Output:
    news/{TICKER}/{YEAR}/{MONTH}/{SLUG}.md  # Individual news articles
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import yfinance as yf
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f'Error: Required package not installed - {e}')
    print('Run: pip install yfinance requests beautifulsoup4 lxml')
    sys.exit(1)


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from news headline."""
    # Remove special characters
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove leading/trailing hyphens and convert to lowercase
    slug = slug.strip('-').lower()
    # Limit to 100 characters
    return slug[:100]


def extract_article_content(html_content: str, url: str) -> str:
    """
    Extract article content from HTML.

    Args:
        html_content: Raw HTML content
        url: Article URL (for context)

    Returns:
        Extracted article content as text
    """
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()

    # Try different selectors for article content
    article_content = None

    # Try common article selectors
    selectors = [
        'article',
        '[data-test="article-body"]',
        '.caas-body',
        '.article-body',
        '.post-content',
        '.entry-content',
        '.news-content',
        'main'
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            article_content = element.get_text(separator='\n', strip=True)
            break

    # If no specific selector found, try to find the largest text block
    if not article_content:
        # Get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            article_content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

    # Clean up the content
    if article_content:
        # Remove very short lines (likely navigation)
        lines = article_content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Keep only substantial lines
                cleaned_lines.append(line)
        article_content = '\n\n'.join(cleaned_lines[:30])  # Limit to first 30 meaningful paragraphs

    return article_content or "Content could not be extracted."

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying functions with exponential backoff."""
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"  → Retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class NewsFetcher:
    """Fetches and manages news data for stocks."""

    def __init__(self, ticker: str = None, tickers: List[str] = None, max_headlines: int = 20):
        """
        Initialize news fetcher.

        Args:
            ticker: Single ticker to fetch
            tickers: Multiple tickers to fetch
            max_headlines: Maximum headlines to fetch per ticker
        """
        self.project_root = get_project_root()
        self.news_dir = self.project_root / 'news'
        self.max_headlines = max_headlines
        self.results = {}
        self.errors = []

        # Determine tickers to fetch
        if ticker:
            self.tickers = [ticker.upper()]
        elif tickers:
            self.tickers = [t.upper() for t in tickers]
        else:
            self.tickers = []

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def fetch_ticker_news(self, ticker: str) -> List[Dict]:
        """
        Fetch news headlines for a single ticker with automatic retry.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of news headline dictionaries
        """
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news or len(news) == 0:
            print(f"✗ {ticker} - No news available")
            return []

        # Process headlines (filter out invalid entries)
        headlines = []
        for item in news[:self.max_headlines]:
            # Handle nested structure: item['content'] contains actual news data
            content = item.get('content', {}) if isinstance(item, dict) else item

            # Extract data from content dict or from item directly
            title = content.get('title', '').strip()
            link = content.get('clickThroughUrl', {}).get('url', '') if isinstance(content.get('clickThroughUrl'), dict) else content.get('clickThroughUrl', '')
            source = content.get('provider', {}).get('displayName', 'Unknown') if isinstance(content.get('provider'), dict) else content.get('provider', 'Unknown')
            pub_date_str = content.get('pubDate', '')

            # Skip invalid entries
            if not title or title == 'No title' or not link:
                continue

            # Parse published date
            if pub_date_str:
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    published_date = pub_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    published_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                published_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            headline = {
                'title': title,
                'link': link,
                'published_date': published_date,
                'source': source,
                'type': content.get('contentType', 'article')
            }
            headlines.append(headline)

        print(f"✓ {ticker} - Fetched {len(headlines)} headlines")
        return headlines

    def article_exists(self, ticker: str, headline: Dict) -> bool:
        """
        Check if an article already exists by matching URL or title+date.

        Args:
            ticker: Stock ticker symbol
            headline: Headline dictionary

        Returns:
            True if article exists, False otherwise
        """
        url = headline.get('link', '')
        title = headline.get('title', '')
        pub_date_str = headline.get('published_date', '')

        # Parse published date to get year/month
        try:
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pub_date = datetime.now()

        year = pub_date.strftime('%Y')
        month = pub_date.strftime('%m')

        # Check the news directory for this ticker/year/month
        ticker_news_dir = self.news_dir / ticker / year / month

        if not ticker_news_dir.exists():
            return False

        # Check all existing articles for duplicate URL or title+date
        for existing_file in ticker_news_dir.glob('*.md'):
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract URL from frontmatter
                    if url and f'url: {url}' in content:
                        return True
                    # Extract title from frontmatter (secondary check)
                    if title and f'title: {title}' in content and pub_date_str in content:
                        return True
            except Exception:
                continue

        return False

    def fetch_article_content(self, url: str) -> str:
        """
        Fetch article content from URL.

        Args:
            url: Article URL

        Returns:
            Extracted article content or error message
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return extract_article_content(response.text, url)
        except Exception as e:
            return f"Content could not be fetched: {str(e)}"

    def save_ticker_news(self, ticker: str, headlines: List[Dict]) -> List[Path]:
        """
        Save news data for a ticker as individual markdown files.

        Args:
            ticker: Stock ticker symbol
            headlines: List of headline dictionaries

        Returns:
            List of paths to saved files
        """
        saved_paths = []
        skipped_count = 0

        for headline in headlines:
            # Check for duplicate before processing
            if self.article_exists(ticker, headline):
                skipped_count += 1
                continue

            title = headline.get('title', 'untitled')
            slug = generate_slug(title)
            url = headline.get('link', '')

            pub_date_str = headline.get('published_date', '')
            try:
                pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Fallback to current date if parsing fails
                pub_date = datetime.now()

            year = pub_date.strftime('%Y')
            month = pub_date.strftime('%m')

            # Create directory structure
            ticker_news_dir = self.news_dir / ticker / year / month
            ticker_news_dir.mkdir(parents=True, exist_ok=True)

            filepath = ticker_news_dir / f"{slug}.md"

            # Handle duplicate slugs (edge case: same title from different sources)
            counter = 1
            while filepath.exists():
                filepath = ticker_news_dir / f"{slug}-{counter}.md"
                counter += 1

            # Fetch article content
            article_content = self.fetch_article_content(url)

            # Write markdown with frontmatter and content
            content = f"""---
title: {title}
source: {headline.get('source', 'Unknown')}
published_date: {pub_date_str}
url: {url}
---

# {title}

**Source**: {headline.get('source', 'Unknown')}
**Published**: {pub_date_str}
**Link**: {url}

{article_content}
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            saved_paths.append(filepath)

            # Rate limiting - be respectful to servers
            import time
            time.sleep(1)

        if skipped_count > 0:
            print(f"  → Skipped {skipped_count} duplicate articles")

        return saved_paths

    def fetch_all(self) -> Dict:
        """
        Fetch news for all tickers.

        Returns:
            Summary of fetch results
        """
        if not self.tickers:
            print("Error: No tickers specified. Use --ticker or --tickers")
            sys.exit(1)

        print(f"\nFetching news for {len(self.tickers)} stocks (max {self.max_headlines} headlines each)...\n")
        print("=" * 60)

        successful = 0
        failed = 0

        for ticker in self.tickers:
            # Fetch news headlines with error handling
            try:
                headlines = self.fetch_ticker_news(ticker)
            except Exception as e:
                error_msg = f"{ticker} - {str(e)}"
                self.errors.append(error_msg)
                print(f"✗ {ticker} - ERROR: {e} (after retries)")
                headlines = []

            if headlines:
                # Save to files
                saved_paths = self.save_ticker_news(ticker, headlines)

                self.results[ticker] = {
                    'status': 'success',
                    'headline_count': len(headlines),
                    'files_saved': len(saved_paths),
                    'latest_headline': headlines[0]['title'] if headlines else None
                }
                successful += 1
            else:
                self.results[ticker] = {
                    'status': 'no_news',
                    'headline_count': 0
                }
                failed += 1

        # Print summary
        print("\n" + "=" * 60)
        print(f"SUMMARY: {successful} successful, {failed} no news")
        print("=" * 60)

        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")

        return {
            'timestamp': datetime.now().isoformat(),
            'tickers_fetched': len(self.tickers),
            'successful': successful,
            'failed': failed,
            'results': self.results
        }


def main():
    """Main entry point for news fetching."""
    parser = argparse.ArgumentParser(
        description='Fetch news for stocks from yfinance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_news.py --ticker NVDA
  python fetch_news.py --tickers NVDA,AAPL,MSFT --limit 30
        """
    )

    parser.add_argument('--ticker', type=str, help='Fetch news for a single ticker')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--limit', type=int, default=20,
                       help='Maximum headlines per ticker (default: 20)')

    args = parser.parse_args()

    try:
        fetcher = NewsFetcher(
            ticker=args.ticker,
            tickers=args.tickers.split(',') if args.tickers else None,
            max_headlines=args.limit
        )
        summary = fetcher.fetch_all()

        # Output as JSON
        print(json.dumps(summary, indent=2))

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
