#!/usr/bin/env python3
"""
Reassess investment thesis using LLM based on fresh news and price action.

This script generates a prompt for LLM-based thesis reassessment.
NOTE: The actual LLM analysis will be done by the agent when invoking the skill.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude"))

from shared.data_access import DataAccess


def generate_reassessment_prompt(
    ticker: str,
    news: List[Dict],
    price_data: Dict,
    existing_thesis: Optional[str] = None
) -> str:
    """
    Generate LLM prompt for thesis reassessment.

    Args:
        ticker: Stock symbol
        news: List of latest news headlines (max 5)
        price_data: Current price info with change %
        existing_thesis: Content from thesis.md file (if exists)

    Returns:
        Prompt string for LLM
    """
    # Format news as bullets
    news_bullets = ""
    if news:
        for article in news[:5]:
            headline = article.get("headline", "No headline")
            age = article.get("age_hours", 0)
            age_str = f"{age:.0f}h ago" if age < 24 else f"{age/24:.1f}d ago"
            news_bullets += f"• {headline} ({age_str})\n"
    else:
        news_bullets = "No recent news available.\n"

    # Format price action
    price = price_data.get("price", "N/A")
    change_pct = price_data.get("change_pct", 0)
    price_str = f"${price:.2f}" if isinstance(price, (int, float)) else price
    change_str = f"{change_pct:+.1f}%" if isinstance(change_pct, (int, float)) else "N/A"

    price_action = f"Price: {price_str} (Daily Change: {change_str})"

    # Format existing thesis summary
    thesis_summary = existing_thesis[:500] if existing_thesis else "No existing thesis found."
    thesis_summary = thesis_summary.replace("\n", " ").strip()

    # Build prompt
    prompt = f"""You are assessing the validity of an investment thesis for {ticker.upper()} based on fresh data.

EXISTING THESIS (if available):
{thesis_summary}

LATEST NEWS (last 24h):
{news_bullets}

CURRENT PRICE ACTION:
{price_action}

ASSESSMENT TASK:
Based on the fresh news and price action, determine if the investment thesis remains VALID or has become DEAD.

Consider:
- Bullish catalysts: positive news, earnings beats, partnerships, upgrades
- Bearish signals: earnings misses, guidance cuts, scandals, competitive threats
- Price action: significant drops (>10%) may indicate broken theses (but distinguish between fear vs fundamental deterioration)

OUTPUT FORMAT (JSON only, no markdown):
{{
  "status": "VALID" | "DEAD" | "WARNING" | "UNKNOWN",
  "rationale": "2-3 sentence explanation",
  "key_changes": ["key change 1", "key change 2"],
  "confidence": "HIGH" | "MEDIUM" | "LOW"
}}

Apply Inertia Principle: Existing positions are VALID unless proven DEAD.
"""

    return prompt


def reassess_thesis_for_ticker(
    ticker: str,
    news: List[Dict],
    price_data: Dict,
    existing_thesis: Optional[str] = None
) -> Dict:
    """
    Reassess thesis validity using LLM.

    NOTE: This function generates the prompt but does NOT call the LLM.
    The actual LLM analysis will be done by the agent when invoking the skill.

    Args:
        ticker: Stock symbol
        news: List of latest news headlines (max 5)
        price_data: Current price info with change %
        existing_thesis: Content from thesis.md file (if exists)

    Returns:
        Dict with status, rationale, key_changes, confidence, and prompt
    """
    # Generate prompt for LLM
    prompt = generate_reassessment_prompt(ticker, news, price_data, existing_thesis)

    # Return placeholder result (actual analysis done by LLM agent)
    return {
        "ticker": ticker.upper(),
        "status": "UNKNOWN",
        "rationale": "LLM analysis pending",
        "key_changes": [],
        "confidence": "LOW",
        "prompt": prompt,
        "thesis_exists": existing_thesis is not None,
        "news_count": len(news),
        "price_available": price_data.get("price") is not None
    }


def batch_reassess_theses(
    holdings: List[Dict],
    news_data: Dict[str, List[Dict]],
    price_data: Dict[str, Dict]
) -> Dict[str, Dict]:
    """
    Batch reassess theses for multiple holdings.

    Args:
        holdings: List of holding dicts with ticker
        news_data: Dict mapping ticker to news articles
        price_data: Dict mapping ticker to price data

    Returns:
        Dict mapping ticker to reassessment results
    """
    da = DataAccess()
    results = {}

    for holding in holdings:
        ticker = holding.get("ticker", "").upper()
        if not ticker:
            continue

        # Get existing thesis
        analytics = da.read_analytics(ticker)
        existing_thesis = analytics.get("thesis")

        # Get news and price data
        ticker_news = news_data.get(ticker, [])
        ticker_price = price_data.get(ticker, {})

        # Reassess
        result = reassess_thesis_for_ticker(
            ticker,
            ticker_news,
            ticker_price,
            existing_thesis
        )

        results[ticker] = result

    return results


def main():
    parser = argparse.ArgumentParser(description="Reassess investment thesis using LLM")
    parser.add_argument("--ticker", type=str, help="Single ticker to reassess")
    parser.add_argument("--tickers", type=str, help="Comma-separated list of tickers")
    parser.add_argument("--format", type=str, default="json", choices=["json", "prompt"], help="Output format")
    args = parser.parse_args()

    if args.ticker:
        tickers = [args.ticker]
    elif args.tickers:
        tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    else:
        print("Error: Must specify --ticker or --tickers", file=sys.stderr)
        sys.exit(1)

    da = DataAccess()

    results = {}
    for ticker in tickers:
        ticker_upper = ticker.upper()

        # Get existing thesis
        analytics = da.read_analytics(ticker_upper)
        existing_thesis = analytics.get("thesis")

        # Get price data (placeholder)
        price_data = {"price": None, "change_pct": None}

        # Get news data (placeholder)
        news_data = []

        # Generate reassessment
        result = reassess_thesis_for_ticker(
            ticker_upper,
            news_data,
            price_data,
            existing_thesis
        )

        if args.format == "prompt":
            print(f"\n{'='*60}\n")
            print(f"PROMPT FOR {ticker_upper}\n")
            print(f"{'='*60}\n")
            print(result["prompt"])
        else:
            results[ticker_upper] = result

    if args.format == "json":
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
