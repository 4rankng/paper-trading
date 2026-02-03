#!/usr/bin/env python3
"""
Get trade log history.

Usage:
    python get_trade_log.py
    python get_trade_log.py --limit 10
    python get_trade_log.py --ticker TCOM
    python get_trade_log.py --portfolio CORE
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from common import get_project_root


def get_trade_log(
    limit: int | None = None,
    ticker: str | None = None,
    portfolio: str | None = None
) -> dict:
    """
    Get trade log history.

    Args:
        limit: Maximum number of trades to return
        ticker: Filter by ticker
        portfolio: Filter by portfolio name

    Returns:
        Dictionary with trade log entries
    """
    trade_log_path = get_project_root() / "trade_log.csv"

    if not trade_log_path.exists():
        return {"status": "success", "count": 0, "trades": []}

    try:
        with open(trade_log_path, "r") as f:
            reader = csv.DictReader(f)
            all_trades = list(reader)

        # Filter by ticker if specified
        if ticker:
            all_trades = [t for t in all_trades if t["ticker"].upper() == ticker.upper()]

        # Filter by portfolio if specified
        if portfolio:
            all_trades = [t for t in all_trades if t.get("portfolio", "LEGACY") == portfolio]

        # Sort by timestamp (most recent first)
        all_trades.sort(key=lambda x: x["timestamp"], reverse=True)

        # Limit results
        if limit and limit > 0:
            all_trades = all_trades[:limit]

        return {"status": "success", "count": len(all_trades), "trades": all_trades}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Get trade log history")
    parser.add_argument("--limit", type=int, help="Limit to N most recent trades")
    parser.add_argument("--ticker", type=str, help="Filter by ticker")
    parser.add_argument("--portfolio", type=str, help="Filter by portfolio name (e.g., CORE, AI_PICKS)")
    parser.add_argument("--format", choices=["json", "human"], default="json", help="Output format")

    args = parser.parse_args()

    result = get_trade_log(args.limit, args.ticker, args.portfolio)

    if args.format == "human":
        if result["status"] == "error":
            print(f"Error: {result['error']}")
            sys.exit(1)

        portfolio_filter = f" | Portfolio: {args.portfolio}" if args.portfolio else ""
        ticker_filter = f" | Ticker: {args.ticker}" if args.ticker else ""
        print(f"Trade Log ({result['count']} entries{portfolio_filter}{ticker_filter})")
        print("=" * 80)
        for t in result["trades"]:
            portfolio_col = f" [{t.get('portfolio', 'N/A')}]" if "portfolio" in t or t.get("portfolio") else ""
            print(f"{t['timestamp']} | {t['ticker']}{portfolio_col} {t['action']:4} | {t['shares']:>6} @ ${t['price']:>7} | {t['reasoning'][:50]}")
    else:
        print(json.dumps(result, indent=2))

    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
