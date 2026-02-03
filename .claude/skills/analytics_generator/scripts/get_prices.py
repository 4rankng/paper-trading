#!/usr/bin/env python3
"""
Get historical price data for analysis.

Usage:
    python get_prices.py --ticker NVDA --period 6M
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add shared module to path
# get_prices.py is at .claude/skills/analytics_generator/scripts/
# parents[0]=scripts, [1]=analytics_generator, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.data_access"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    import pandas as pd
except ImportError:
    print('Error: pandas not installed.')
    print('Run: pip install pandas')
    sys.exit(1)

try:
    from shared.data_access import get_project_root
except ImportError:
    # Fallback for when run from scripts directory directly
    def get_project_root() -> Path:
        """Get project root directory using marker files."""
        p = Path(__file__).resolve()
        markers = ['prices/', '.git/', 'watchlist.json']
        for parent in [p, *p.parents]:
            if any((parent / m).exists() for m in markers):
                return parent
        if ".claude" in p.parts:
            idx = p.parts.index(".claude")
            return Path(*p.parts[:idx])
        raise RuntimeError("Project root not found")


def get_historical_prices(ticker: str, period: str = "6M") -> dict:
    """
    Get historical price data for a ticker.

    Args:
        ticker: Stock ticker symbol
        period: Time period (1M, 3M, 6M, 1Y, 2Y)

    Returns:
        Dictionary with historical price data
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

        # Filter by period
        period_map = {
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '1Y': 365,
            '2Y': 730
        }

        days = period_map.get(period, 180)
        cutoff_date = df.index[-1] - timedelta(days=days)
        df_filtered = df[df.index >= cutoff_date]

        # Convert to list of dicts
        data = []
        for date, row in df_filtered.iterrows():
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(float(row['Open']), 4),
                'high': round(float(row['High']), 4),
                'low': round(float(row['Low']), 4),
                'close': round(float(row['Close']), 4),
                'volume': int(row['Volume'])
            })

        return {
            'status': 'success',
            'ticker': ticker.upper(),
            'period': period,
            'data_points': len(data),
            'start_date': data[0]['date'] if data else None,
            'end_date': data[-1]['date'] if data else None,
            'data': data
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'ticker': ticker.upper()
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Get historical prices for analysis')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker symbol')
    parser.add_argument('--period', default='6M', choices=['1M', '3M', '6M', '1Y', '2Y'],
                       help='Time period (default: 6M)')

    args = parser.parse_args()

    result = get_historical_prices(args.ticker, args.period)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
