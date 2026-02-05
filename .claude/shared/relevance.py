#!/usr/bin/env python3
"""Finance relevance detection for filtering web searches."""

import re
from typing import List, Set


# Common ticker symbol patterns
TICKER_PATTERN = r'\$?[A-Z]{1,5}\b'

# Finance and investing keywords
FINANCE_KEYWORDS: Set[str] = {
    # Basic terms
    'stock', 'stocks', 'share', 'shares', 'equity', 'equities',
    'earnings', 'revenue', 'profit', 'loss', 'dividend', 'dividends',
    'portfolio', 'investing', 'investment', 'investor', 'trading', 'trader',

    # Market terms
    'market', 'markets', 'bull', 'bear', 'bullish', 'bearish',
    'volatility', 'index', 'indices', 'dow', 's&p', 'nasdaq',
    'rally', 'crash', 'correction', 'bubble',

    # Analysis
    'technical', 'fundamental', 'valuation', 'pe ratio', 'eps',
    'analyst', 'upgrade', 'downgrade', 'rating', 'forecast',

    # Economic/Policy
    'fed', 'federal reserve', 'interest rate', 'inflation', 'gdp',
    'recession', 'economic', 'economy', 'monetary', 'fiscal',

    # Options/derivatives
    'option', 'options', 'call', 'put', 'strike', 'expiry',
    'futures', 'derivative',

    # Company actions
    'ipo', 'merger', 'acquisition', 'buyout', 'spinoff',
    'split', 'buyback', 'dividend',

    # Crypto (optional, can be enabled)
    'bitcoin', 'ethereum', 'crypto', 'blockchain',
}

# Non-finance keywords to exclude (generic searches)
EXCLUDE_KEYWORDS: Set[str] = {
    'weather', 'temperature', 'forecast weather',
    'recipe', 'cooking', 'food',
    'movie', 'film', 'cinema',
    'game', 'gaming', 'play',
    'sports', 'score', 'team',
    'celebrity', 'gossip',
}


def extract_tickers(text: str) -> List[str]:
    """Extract potential ticker symbols from text.

    Args:
        text: Input text

    Returns:
        List of potential ticker symbols (uppercase, 1-5 chars)
    """
    matches = re.findall(TICKER_PATTERN, text)
    # Remove $ prefix if present and filter to valid ticker lengths
    tickers = [m.replace('$', '').upper() for m in matches if 1 <= len(m.replace('$', '')) <= 5]

    # Filter out common English words
    common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS'}
    tickers = [t for t in tickers if t not in common_words]

    return list(set(tickers))  # Deduplicate


def is_finance_relevant(text: str) -> bool:
    """Check if text contains finance-related content.

    A text is considered finance-relevant if:
    1. It contains ticker symbols (e.g., AAPL, $NVDA), OR
    2. It contains finance keywords

    Args:
        text: Input text to check

    Returns:
        True if finance-relevant, False otherwise
    """
    if not text or len(text.strip()) < 10:
        return False

    text_lower = text.lower()

    # Check for exclusion keywords (non-finance content)
    for exclude_kw in EXCLUDE_KEYWORDS:
        if exclude_kw in text_lower:
            return False

    # Check for ticker symbols
    tickers = extract_tickers(text)
    if tickers:
        return True

    # Check for finance keywords
    has_finance_kw = any(kw in text_lower for kw in FINANCE_KEYWORDS)

    return has_finance_kw


def get_relevance_score(text: str) -> float:
    """Calculate relevance score for finance content.

    Returns a score between 0.0 and 1.0 based on:
    - Number of ticker symbols found
    - Number of finance keywords found

    Args:
        text: Input text

    Returns:
        Relevance score (0.0 to 1.0)
    """
    if not text or len(text.strip()) < 10:
        return 0.0

    text_lower = text.lower()

    # Check for exclusion keywords
    for exclude_kw in EXCLUDE_KEYWORDS:
        if exclude_kw in text_lower:
            return 0.0

    score = 0.0

    # Ticker symbols (high relevance)
    tickers = extract_tickers(text)
    if tickers:
        score += min(len(tickers) * 0.3, 0.6)  # Max 0.6 from tickers

    # Finance keywords (medium relevance)
    kw_count = sum(1 for kw in FINANCE_KEYWORDS if kw in text_lower)
    if kw_count > 0:
        score += min(kw_count * 0.1, 0.4)  # Max 0.4 from keywords

    return min(score, 1.0)


def classify_content_type(text: str) -> str:
    """Classify the type of finance content.

    Args:
        text: Input text

    Returns:
        One of: 'news', 'analysis', 'market_data', 'other'
    """
    text_lower = text.lower()

    # Check for news indicators
    news_keywords = {'breaking', 'reported', 'announced', 'sources',
                     'news', 'update', 'reported that', 'according to'}
    if any(kw in text_lower for kw in news_keywords):
        return 'news'

    # Check for analysis indicators
    analysis_keywords = {'analysis', 'technical', 'fundamental',
                         'valuation', 'recommend', 'target price'}
    if any(kw in text_lower for kw in analysis_keywords):
        return 'analysis'

    # Check for market data
    market_keywords = {'index', 'futures', 'pre-market', 'after-hours',
                       'volume', 'price', 'closed at'}
    if any(kw in text_lower for kw in market_keywords):
        return 'market_data'

    return 'other'
