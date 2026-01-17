#!/usr/bin/env python3
"""
Get trade log history.

Usage:
    python get_trade_log.py
    python get_trade_log.py --limit 10
    python get_trade_log.py --ticker TCOM
"""
import argparse
import csv
import json
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


def get_trade_log(limit: int = None, ticker: str = None) -> dict:
    """
    Get trade log history.

    Args:
        limit: Maximum number of trades to return
        ticker: Filter by ticker

    Returns:
        Dictionary with trade log entries
    """
    project_root = get_project_root()
    trade_log_path = project_root / 'trade_log.csv'

    if not trade_log_path.exists():
        return {
            'status': 'success',
            'count': 0,
            'trades': []
        }

    try:
        with open(trade_log_path, 'r') as f:
            reader = csv.DictReader(f)
            all_trades = list(reader)

        # Filter by ticker if specified
        if ticker:
            all_trades = [t for t in all_trades if t['ticker'].upper() == ticker.upper()]

        # Sort by timestamp (most recent first)
        all_trades.sort(key=lambda x: x['timestamp'], reverse=True)

        # Limit results
        if limit and limit > 0:
            all_trades = all_trades[:limit]

        return {
            'status': 'success',
            'count': len(all_trades),
            'trades': all_trades
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Get trade log history')
    parser.add_argument('--limit', type=int, help='Limit to N most recent trades')
    parser.add_argument('--ticker', type=str, help='Filter by ticker')

    args = parser.parse_args()

    result = get_trade_log(args.limit, args.ticker)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
