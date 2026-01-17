#!/usr/bin/env python3
"""
Get current (latest) price for a ticker.

Usage:
    python get_price.py --ticker NVDA
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print('Error: pandas not installed.')
    print('Run: pip install pandas')
    sys.exit(1)


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def get_latest_price(ticker: str) -> dict:
    """
    Get the latest price for a ticker from prices/{TICKER}.csv.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with latest price data
    """
    project_root = get_project_root()
    prices_dir = project_root / 'prices'
    csv_path = prices_dir / f"{ticker.upper()}.csv"

    if not csv_path.exists():
        return {
            'status': 'error',
            'error': f'Price file not found for {ticker}',
            'file': str(csv_path.relative_to(project_root))
        }

    try:
        df = pd.read_csv(csv_path, index_col='date', parse_dates=True)

        if df.empty:
            return {
                'status': 'error',
                'error': f'Price file is empty for {ticker}'
            }

        # Get latest row
        latest = df.iloc[-1]

        return {
            'status': 'success',
            'ticker': ticker.upper(),
            'date': latest.name.strftime('%Y-%m-%d'),
            'open': round(float(latest['Open']), 4),
            'high': round(float(latest['High']), 4),
            'low': round(float(latest['Low']), 4),
            'close': round(float(latest['Close']), 4),
            'volume': int(latest['Volume']),
            'data_points': len(df)
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'ticker': ticker.upper()
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Get current price for a ticker')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker symbol')

    args = parser.parse_args()

    result = get_latest_price(args.ticker)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
