#!/usr/bin/env python3
"""
Investment Type Classifier

Classifies stocks as "compounder" or "moonshot" for proper scoring system selection.

COMPOUNDER: Proven, profitable businesses targeting 15-30% CAGR
- Use Quality Compound Scorer
- Position size: 10-20%
- Time horizon: 5-10 years

MOONSHOT: Speculative, high-growth stocks targeting 5-10x
- Use Multi-Bagger Hunter
- Position size: 2-5% max
- Time horizon: 3-7 years
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
WATCHLIST_PATH = PROJECT_ROOT / "watchlist.json"


def classify_from_data(ticker: str, data: Dict) -> str:
    """Classify a stock based on available watchlist/analytical data."""

    # Direct classification if explicitly stated
    if data.get("strategy") == "speculative":
        return "moonshot"

    # Check fundamentals-based indicators
    profit_margin = data.get("profit_margin")
    operating_margin = data.get("operating_margin")
    pe_ratio = data.get("pe_ratio")
    market_cap = data.get("market_cap")
    revenue_growth = data.get("revenue_growth_yoy")

    # Moonshot indicators (speculative)
    moonshot_signals = 0
    compounder_signals = 0

    # High revenue growth but unprofitable = moonshot
    if revenue_growth:
        if revenue_growth > 50 and (profit_margin or 0) < 0:
            moonshot_signals += 2
        elif revenue_growth > 30 and (operating_margin or 0) < 0:
            moonshot_signals += 1

    # Negative margins = moonshot (unless turnaround)
    if profit_margin and profit_margin < -10:
        moonshot_signals += 2
    elif operating_margin and operating_margin < -10:
        moonshot_signals += 2

    # Small cap + negative = moonshot
    if market_cap and market_cap < 2_000_000_000:  # <$2B
        if profit_margin and profit_margin < 0:
            moonshot_signals += 2

    # High P/E but strong margins = compounder (quality growth)
    if pe_ratio and pe_ratio > 30:
        if operating_margin and operating_margin > 15:
            compounder_signals += 1

    # Strong margins + profitability = compounder
    if operating_margin and operating_margin > 15:
        compounder_signals += 2
    if profit_margin and profit_margin > 15:
        compounder_signals += 2

    # Large cap + profitable = compounder
    if market_cap and market_cap > 50_000_000_000:  # >$50B
        if profit_margin and profit_margin > 5:
            compounder_signals += 1

    # Known compounders (large-cap tech, dividend payers)
    known_compounders = ["MSFT", "AAPL", "GOOGL", "GOOG", "META", "AMZN", "NVDA",
                         "TSM", "JPM", "BAC", "WFC", "GS", "BLK", "V", "MA", "HD", "KO"]
    if ticker in known_compounders:
        compounder_signals += 3

    # Known moonshots (speculative sectors)
    if data.get("industry", "").lower() in ["biotechnology", "biotech"]:
        moonshot_signals += 1

    # Decision
    if moonshot_signals >= 2:
        return "moonshot"
    elif compounder_signals >= 2:
        return "compounder"
    elif moonshot_signals > compounder_signals:
        return "moonshot"
    else:
        return "compounder"  # Default


def classify_from_thesis(ticker: str, thesis_text: str) -> Optional[str]:
    """Classify based on investment thesis content."""
    if not thesis_text:
        return None

    thesis_lower = thesis_text.lower()

    # Moonshot keywords
    moonshot_keywords = [
        "hype_machine", "speculative", "binary outcome", "pre-revenue",
        "unproven", "early-stage", "revolutionary", "paradigm shift",
        "moonshot", "multibagger", "10x", "turnaround", "development",
    ]

    # Compounder keywords
    compounder_keywords = [
        "compounder", "quality growth", "wide moat", "dividend",
        "aristocrat", "consistent", "predictable", "steady",
        "proven business", "established", "market leader",
    ]

    moonshot_count = sum(1 for kw in moonshot_keywords if kw in thesis_lower)
    compounder_count = sum(1 for kw in compounder_keywords if kw in thesis_lower)

    if moonshot_count >= 2:
        return "moonshot"
    elif compounder_count >= 2:
        return "compounder"

    return None


def classify_from_fundamentals(ticker: str, fundamental_text: str) -> Optional[str]:
    """Classify based on fundamental analysis."""
    if not fundamental_text:
        return None

    fund_lower = fundamental_text.lower()

    # Check for moonshot characteristics
    negative_indicators = [
        "unprofitable", "negative operating margin", "burn rate",
        "pre-revenue", "net loss", "not yet profitable",
    ]

    positive_indicators = [
        "strong margins", "positive free cash flow", "high roe",
        "dividend yield", "profit margins", "return on equity",
    ]

    negative_count = sum(1 for kw in negative_indicators if kw in fund_lower)
    positive_count = sum(1 for kw in positive_indicators if kw in fund_lower)

    if negative_count >= 2 and positive_count == 0:
        return "moonshot"
    elif positive_count >= 2 and negative_count == 0:
        return "compounder"

    return None


def auto_classify_watchlist():
    """Auto-classify all watchlist entries."""

    if not WATCHLIST_PATH.exists():
        print(f"Error: {WATCHLIST_PATH} not found")
        return

    with open(WATCHLIST_PATH) as f:
        watchlist = json.load(f)

    classified = 0
    for entry in watchlist:
        ticker = entry.get("ticker")
        if not ticker or entry.get("investment_type"):
            continue

        # Get classification
        classification = classify_from_data(ticker, entry)

        # Check thesis if available
        thesis_path = PROJECT_ROOT / "analytics" / ticker / f"{ticker}_investment_thesis.md"
        if thesis_path.exists():
            thesis_text = thesis_path.read_text()
            thesis_classification = classify_from_thesis(ticker, thesis_text)
            if thesis_classification:
                classification = thesis_classification

        # Set classification
        entry["investment_type"] = classification
        classified += 1

    # Write back
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(watchlist, f, indent=2)

    print(f"Classified {classified} stocks in watchlist")
    return watchlist


def print_classification_summary():
    """Print summary of classifications."""

    if not WATCHLIST_PATH.exists():
        print(f"Error: {WATCHLIST_PATH} not found")
        return

    with open(WATCHLIST_PATH) as f:
        watchlist = json.load(f)

    compounders = []
    moonshots = []
    unclassified = []

    for entry in watchlist:
        inv_type = entry.get("investment_type")
        ticker = entry.get("ticker")
        name = entry.get("name", "")
        price = entry.get("price")

        if inv_type == "compounder":
            compounders.append((ticker, name, price))
        elif inv_type == "moonshot":
            moonshots.append((ticker, name, price))
        else:
            unclassified.append((ticker, name, price))

    print("\n" + "="*70)
    print("WATCHLIST CLASSIFICATION SUMMARY")
    print("="*70)

    print(f"\n📈 COMPOUNDERS ({len(compounders)}):")
    print("-" * 70)
    for ticker, name, price in compounders:
        price_str = f" ${price}" if price else ""
        print(f"  {ticker:<8} {name[:40]:<40}{price_str}")

    print(f"\n🚀 MOONSHOTS ({len(moonshots)}):")
    print("-" * 70)
    for ticker, name, price in moonshots:
        price_str = f" ${price}" if price else ""
        print(f"  {ticker:<8} {name[:40]:<40}{price_str}")

    print(f"\n❓ UNCLASSIFIED ({len(unclassified)}):")
    print("-" * 70)
    for ticker, name, price in unclassified:
        price_str = f" ${price}" if price else ""
        print(f"  {ticker:<8} {name[:40]:<40}{price_str}")

    print("\n" + "="*70)
    print(f"Total: {len(watchlist)} stocks")
    print("="*70)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_classification_summary()
    else:
        auto_classify_watchlist()
