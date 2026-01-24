#!/usr/bin/env python3
"""
Fetch historical stock price data and update prices/{TICKER}.csv.

This script fetches historical OHLCV data from yfinance and manages
incremental updates to CSV files in the prices/ directory.

Usage:
    python fetch_prices.py --ticker NVDA
    python fetch_prices.py --tickers NVDA,AAPL,MSFT

Output:
    prices/{TICKER}.csv  # Daily OHLCV data (append-only)

Behavior:
    First fetch: 2 years of data
    Subsequent: Incremental append (gap >30 days triggers full refresh)
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print('Error: Required packages not installed.')
    print('Run: pip install yfinance pandas')
    sys.exit(1)


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


class PriceFetcher:
    """Fetches and manages historical price data for stocks."""

    def __init__(self, period: str = "2y", ticker: str = None, tickers: List[str] = None):
        """
        Initialize price fetcher.

        Args:
            period: Time period for historical data ("6mo", "1y", "2y")
            ticker: Single ticker to fetch
            tickers: Multiple tickers to fetch
        """
        self.project_root = get_project_root()
        self.prices_dir = self.project_root / 'prices'
        self.period = period if period in ["6mo", "1y", "2y"] else "2y"
        self.results = {}
        self.errors = []

        # Determine tickers to fetch
        if ticker:
            self.tickers = [ticker.upper()]
        elif tickers:
            self.tickers = [t.upper() for t in tickers]
        else:
            self.tickers = []

    def _get_last_date_from_csv(self, ticker: str) -> Optional[str]:
        """
        Get the last date from existing CSV file.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Last date string (YYYY-MM-DD) or None if file doesn't exist
        """
        csv_path = self.prices_dir / f"{ticker}.csv"
        if not csv_path.exists():
            return None

        try:
            df = pd.read_csv(csv_path, index_col='date', parse_dates=True)
            if not df.empty:
                return df.index[-1].strftime('%Y-%m-%d')
        except Exception as e:
            print(f"  Warning: Could not read existing CSV: {e}")

        return None

    def fetch_ticker_history(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a single ticker with incremental update support.

        If historical data exists, only fetch new days since last update.
        If gap > 30 days or file doesn't exist, fetch full period.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with historical data or None if failed/already current
        """
        try:
            stock = yf.Ticker(ticker)

            # Check for existing data to do incremental update
            last_date = self._get_last_date_from_csv(ticker)

            if last_date:
                # Calculate days since last update
                last_dt = datetime.strptime(last_date, '%Y-%m-%d')
                today = datetime.now().date()
                days_since = (today - last_dt.date()).days

                # If gap is small (weekend/holiday), do incremental fetch
                if 0 < days_since <= 30:
                    # Fetch only new data since last date
                    start_date = (last_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                    end_date = today.strftime('%Y-%m-%d')

                    print(f"  → Incremental update: {start_date} to {end_date} ({days_since} days)")
                    hist = stock.history(start=start_date, end=end_date)

                    if hist.empty:
                        # No new trading days (weekend/holiday)
                        print(f"  ✓ {ticker} - Already current as of {last_date}")
                        return None

                    print(f"✓ {ticker} - Fetched {len(hist)} new days (incremental)")
                    return hist
                elif days_since <= 0:
                    # Data is current
                    print(f"  ✓ {ticker} - Already current as of {last_date}")
                    return None
                else:
                    # Gap too large, do full fetch
                    print(f"  → Full refresh: gap is {days_since} days (>30)")
                    hist = stock.history(period=self.period)
            else:
                # No existing file, fetch full period
                print(f"  → First fetch: {self.period} of data")
                hist = stock.history(period=self.period)

            if hist.empty:
                print(f"✗ {ticker} - No historical data available")
                return None

            print(f"✓ {ticker} - Fetched {len(hist)} days of data")
            return hist

        except Exception as e:
            error_msg = f"{ticker} - {str(e)}"
            self.errors.append(error_msg)
            print(f"✗ {ticker} - ERROR: {e}")
            return None

    def save_to_csv(self, ticker: str, hist: pd.DataFrame) -> Path:
        """
        Save historical data to CSV (append mode for incremental updates).

        Args:
            ticker: Stock ticker symbol
            hist: DataFrame with historical data

        Returns:
            Path to saved CSV file
        """
        csv_path = self.prices_dir / f"{ticker}.csv"
        self.prices_dir.mkdir(exist_ok=True)

        # Prepare DataFrame for CSV
        df = hist.copy()
        df.index.name = 'date'
        df.index = df.index.strftime('%Y-%m-%d')
        df = df.round({'Open': 4, 'High': 4, 'Low': 4, 'Close': 4, 'Volume': 0})

        # Check if file exists to determine write mode
        if csv_path.exists():
            # Read existing CSV to find last date
            existing_df = pd.read_csv(csv_path, index_col='date', parse_dates=True)
            last_date = existing_df.index[-1]

            # Filter new data to only dates after last_date
            # Convert string index to datetime for comparison
            df_index_dt = pd.to_datetime(df.index)
            new_df = df[df_index_dt > last_date]

            if not new_df.empty:
                # Append new data
                new_df.to_csv(csv_path, mode='a', header=False)
                print(f"  → Appended {len(new_df)} new rows to {csv_path.name}")
            else:
                print(f"  → No new data to append (already current)")
        else:
            # New file - write with header
            df.to_csv(csv_path, mode='w')
            print(f"  → Created new CSV file {csv_path.name} with {len(df)} rows")

        return csv_path

    def fetch_all(self) -> Dict:
        """
        Fetch historical data for all tickers.

        Returns:
            Summary of fetch results
        """
        if not self.tickers:
            print("Error: No tickers specified. Use --ticker or --tickers")
            sys.exit(1)

        print(f"\nFetching {self.period} of historical data for {len(self.tickers)} stocks...\n")
        print("=" * 60)

        successful = 0
        failed = 0

        for ticker in self.tickers:
            # Fetch historical data
            hist_df = self.fetch_ticker_history(ticker)

            if hist_df is not None:
                # Save to file
                filepath = self.save_to_csv(ticker, hist_df)

                # Get latest price
                latest_price = round(float(hist_df['Close'].iloc[-1]), 4)

                self.results[ticker] = {
                    'status': 'success',
                    'file': str(filepath.relative_to(self.project_root)),
                    'data_points': len(hist_df),
                    'latest_price': latest_price
                }
                successful += 1
            else:
                self.results[ticker] = {
                    'status': 'skipped',
                    'error': 'No new data'
                }
                failed += 1

        # Print summary
        print("\n" + "=" * 60)
        print(f"SUMMARY: {successful} successful, {failed} failed")
        print("=" * 60)

        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")

        return {
            'timestamp': datetime.now().isoformat(),
            'period': self.period,
            'tickers_fetched': len(self.tickers),
            'successful': successful,
            'failed': failed,
            'results': self.results
        }


def main():
    """Main entry point for price fetching."""
    parser = argparse.ArgumentParser(
        description='Fetch historical price data for stocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_prices.py --ticker NVDA
  python fetch_prices.py --tickers NVDA,AAPL,MSFT
  python fetch_prices.py NVDA AAPL MSFT
  python fetch_prices.py --ticker TCOM --period 1y
        """
    )

    parser.add_argument('tickers_pos', nargs='*', help='Tickers as positional arguments')
    parser.add_argument('--ticker', type=str, help='Fetch data for a single ticker')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--period', default='2y', choices=['6mo', '1y', '2y'],
                       help='Time period to fetch (default: 2y)')

    args = parser.parse_args()

    # Collect tickers from all sources: positional, --ticker, --tickers
    all_tickers = []
    if args.tickers_pos:
        all_tickers.extend(args.tickers_pos)
    if args.ticker:
        all_tickers.append(args.ticker)
    if args.tickers:
        all_tickers.extend(args.tickers.split(','))

    try:
        fetcher = PriceFetcher(period=args.period, ticker=None, tickers=all_tickers if all_tickers else None)
        summary = fetcher.fetch_all()

        # Output as JSON
        print(json.dumps(summary, indent=2))

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
