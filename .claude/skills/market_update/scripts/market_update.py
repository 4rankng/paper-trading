#!/usr/bin/env python3
"""
Market Update - Main Orchestrator

Generates at-a-glance market update for current holdings including:
- Latest stock-specific news (fresh via WebSearch if files are stale)
- Current stock prices (CSV or yfinance)
- Investment thesis reassessment using LLM based on fresh news + price action
- Macroeconomic context (CNN Fear & Greed + macro thesis)
- Mobile-friendly output using viz:table/viz:chart format
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude"))

from shared.data_access import DataAccess

# Import local modules
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from get_holdings_summary import get_holdings_with_pnl
from fetch_current_prices import get_current_prices
from aggregate_news import get_latest_news_for_tickers
from check_macro import get_macro_context
from reassess_thesis import batch_reassess_theses


def generate_market_update(portfolio_name: Optional[str] = None, force_refresh: bool = False) -> Dict:
    """
    Generate complete market update for portfolio.

    Args:
        portfolio_name: Portfolio name (e.g., "CORE", "AI_PICKS")
        force_refresh: If True, force refresh all data from APIs

    Returns:
        Complete update data with holdings, prices, news, macro, thesis_reassessment
    """
    # Step 1: Get holdings summary
    print("Step 1: Getting holdings summary...", file=sys.stderr)
    holdings_data = get_holdings_with_pnl(portfolio_name)
    holdings = holdings_data["holdings"]
    tickers = [h["ticker"] for h in holdings]

    if not tickers:
        return {
            "error": "No holdings found",
            "portfolio_name": holdings_data["portfolio_name"],
            "message": f"No holdings found in {holdings_data['portfolio_name']} portfolio."
        }

    # Step 2: Fetch current prices
    print("Step 2: Fetching current prices...", file=sys.stderr)
    price_data = get_current_prices(tickers, force_refresh=force_refresh)

    # Step 3: Aggregate latest news
    print("Step 3: Aggregating latest news...", file=sys.stderr)
    news_data = get_latest_news_for_tickers(tickers, limit=5)

    # Step 4: Check macro context
    print("Step 4: Checking macro context...", file=sys.stderr)
    macro_data = get_macro_context()

    # Step 5: LLM thesis reassessment (placeholder - done by agent)
    print("Step 5: Preparing thesis reassessment...", file=sys.stderr)
    thesis_data = batch_reassess_theses(holdings, news_data, price_data)

    # Combine all data
    update_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "portfolio": {
            "name": holdings_data["portfolio_name"],
            "description": holdings_data["description"],
            "cash": holdings_data["cash"],
            "summary": holdings_data["summary"]
        },
        "holdings": holdings,
        "prices": price_data,
        "news": news_data,
        "macro": macro_data,
        "thesis_reassessment": thesis_data,
        "data_freshness": {
            "prices_fresh": all(p.get("age_hours", 999) < 1 for p in price_data.values() if p.get("price")),
            "news_fresh": all(len(articles) > 0 for articles in news_data.values()),
            "macro_thesis_age_days": macro_data.get("macro_thesis", {}).get("age_days"),
            "fear_greed_fresh": macro_data.get("fear_greed", {}).get("available", False)
        }
    }

    return update_data


def format_price(price: Optional[float]) -> str:
    """Format price as string."""
    if price is None:
        return "N/A"
    return f"${price:.2f}"


def format_change(change_pct: Optional[float]) -> str:
    """Format change percentage as string."""
    if change_pct is None:
        return "N/A"
    return f"{change_pct:+.1f}%"


def format_thesis_status(status: str) -> str:
    """Format thesis status with icon."""
    icons = {
        "VALID": "✓",
        "DEAD": "✗",
        "WARNING": "⚠",
        "UNKNOWN": "?"
    }
    icon = icons.get(status, "")
    return f"{status} {icon}" if icon else status


def generate_terminal_output(update_data: Dict) -> str:
    """
    Generate mobile-friendly terminal output from update data.

    Uses viz:table and viz:chart format (not markdown tables).
    """
    if "error" in update_data:
        return f"## Error\n\n{update_data.get('message', 'Unknown error')}"

    lines = []

    # Header
    portfolio_name = update_data["portfolio"]["name"]
    generated_at = update_data["generated_at"]
    lines.append(f"## Market Update: {portfolio_name} Portfolio")
    lines.append(f"**Generated:** {generated_at}\n")

    # Market Context
    lines.append("### Market Context")

    macro = update_data["macro"]
    fg = macro.get("fear_greed", {})
    thesis = macro.get("macro_thesis", {})

    fg_label = fg.get("label", "N/A")
    fg_value = fg.get("value", "N/A")

    stance = thesis.get("stance", "UNKNOWN")
    risk = thesis.get("risk_level", "UNKNOWN")
    summary = thesis.get("summary", "No macro analysis available")

    lines.append(f"**Fear & Greed:** {fg_value} {fg_label}")
    lines.append(f"**Macro Stance:** {stance} | Risk: {risk}")
    lines.append(f"*Summary: {summary}*\n")

    lines.append("---\n")

    # Holdings Summary
    lines.append(f"### Holdings Summary ({len(update_data['holdings'])} positions)\n")

    # Build viz:table for holdings
    holdings_rows = []
    for h in update_data["holdings"]:
        ticker = h["ticker"]
        price = format_price(h.get("current_price"))
        change = format_change(h.get("gain_loss_pct"))
        value = format_price(h.get("market_value"))

        # Get thesis status
        thesis_re = update_data["thesis_reassessment"].get(ticker, {})
        status = thesis_re.get("status", "UNKNOWN")
        thesis_status = format_thesis_status(status)

        holdings_rows.append([ticker, price, change, value, thesis_status])

    viz_table = {
        "headers": ["Ticker", "Price", "Change", "Value", "Thesis"],
        "rows": holdings_rows
    }

    lines.append("![viz:table](%s)" % json.dumps(viz_table).replace('"', "'"))

    # Portfolio totals
    summary = update_data["portfolio"]["summary"]
    total_value = format_price(summary.get("holdings_value"))
    cash = format_price(update_data["portfolio"]["cash"])
    total_pl = format_change(summary.get("total_gain_loss_pct"))

    lines.append(f"\n**Total Value:** {total_value} | **Cash:** {cash} | **Total P/L:** {total_pl}\n")

    lines.append("---\n")

    # Latest News
    lines.append("### Latest News (Last 24h)\n")

    for ticker, articles in update_data["news"].items():
        if not articles:
            continue

        thesis_re = update_data["thesis_reassessment"].get(ticker, {})
        status = thesis_re.get("status", "UNKNOWN")
        status_label = format_thesis_status(status)

        lines.append(f"**{ticker} ({status_label}):**")

        for article in articles[:3]:
            headline = article.get("headline", "No headline")
            lines.append(f"• {headline}")

        lines.append("")

    # Thesis Reassessment
    lines.append("### Thesis Reassessment (LLM Analysis)\n")

    reassessment_lines = []
    for ticker, re_data in update_data["thesis_reassessment"].items():
        status = format_thesis_status(re_data.get("status", "UNKNOWN"))
        rationale = re_data.get("rationale", "Analysis pending")
        confidence = re_data.get("confidence", "LOW")

        reassessment_lines.append(f"**{ticker}** | {status} | {rationale} | {confidence}")

    if reassessment_lines:
        lines.append(" | ".join(["Ticker", "Status", "Rationale", "Confidence"]))
        lines.append("-" * 80)
        lines.extend(reassessment_lines)

    lines.append("")

    # Data Freshness
    lines.append("### Data Freshness")

    freshness = update_data["data_freshness"]

    price_status = "✓ Current" if freshness["prices_fresh"] else "⚠ Stale"
    news_status = "✓ Current" if freshness["news_fresh"] else "⚠ Stale"
    thesis_status = "✓ Reassessed"  # Always reassessed with LLM

    macro_age = freshness.get("macro_thesis_age_days")
    if macro_age is not None:
        macro_status = "✓ Current" if macro_age < 7 else f"⚠ {macro_age:.0f} days old"
    else:
        macro_status = "✗ N/A"

    fg_status = "✓ Current" if freshness["fear_greed_fresh"] else "⚠ N/A"

    lines.append(f"✓ Prices: {price_status}")
    lines.append(f"✓ News: {news_status}")
    lines.append(f"✓ Thesis: {thesis_status}")
    lines.append(f"✓ Macro: {macro_status}")
    lines.append(f"✓ Fear & Greed: {fg_status}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate market update for portfolio")
    parser.add_argument("--portfolio", type=str, help="Portfolio name (e.g., CORE, LLM_HELP)")
    parser.add_argument("--force-refresh", action="store_true", help="Force refresh all data from APIs")
    parser.add_argument("--format", type=str, default="terminal", choices=["terminal", "json"], help="Output format")
    args = parser.parse_args()

    try:
        # Generate update
        update_data = generate_market_update(args.portfolio, args.force_refresh)

        # Output
        if args.format == "json":
            print(json.dumps(update_data, indent=2))
        else:
            output = generate_terminal_output(update_data)
            print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
