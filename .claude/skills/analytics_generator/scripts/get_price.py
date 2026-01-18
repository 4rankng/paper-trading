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


def get_latest_prices(tickers: list) -> dict:
    """
    Get the latest prices for multiple tickers.

    Args:
        tickers: List of stock ticker symbols

    Returns:
        Dictionary with results for all tickers
    """
    results = {}
    errors = []

    for ticker in tickers:
        result = get_latest_price(ticker.upper())
        results[ticker.upper()] = result
        if result['status'] == 'error':
            errors.append(ticker.upper())

    return {
        'results': results,
        'successful': len(tickers) - len(errors),
        'failed': len(errors),
        'errors': errors
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Get current price for tickers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_price.py --ticker NVDA
  python get_price.py --tickers NVDA,AAPL,MSFT
  python get_price.py NVDA AAPL MSFT
        """
    )
    parser.add_argument('tickers_pos', nargs='*', help='Tickers as positional arguments')
    parser.add_argument('--ticker', type=str, help='Single ticker symbol')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--format', choices=['json', 'compact'], default='json',
                       help='Output format (default: json)')

    args = parser.parse_args()

    # Collect tickers from all sources
    all_tickers = []
    if args.tickers_pos:
        all_tickers.extend(args.tickers_pos)
    if args.ticker:
        all_tickers.append(args.ticker)
    if args.tickers:
        all_tickers.extend(args.tickers.split(','))

    if not all_tickers:
        parser.error("--ticker, --tickers, or positional tickers required")

    # Single ticker mode - legacy output
    if len(all_tickers) == 1:
        result = get_latest_price(all_tickers[0])
        print(json.dumps(result, indent=2))
        if result['status'] == 'error':
            sys.exit(1)
        return

    # Multiple tickers mode
    result = get_latest_prices(all_tickers)

    if args.format == 'compact':
        # Compact output for piping
        for ticker, data in result['results'].items():
            if data['status'] == 'success':
                print(f"{ticker}: ${data['close']} ({data['date']})")
            else:
                print(f"{ticker}: ERROR - {data.get('error', 'Unknown error')}")
    else:
        print(json.dumps(result, indent=2))

    if result['failed'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
