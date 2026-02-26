#!/usr/bin/env python3
"""
Fetch current prices for holdings tickers.

This script gets current prices from CSV files (if fresh) or yfinance (if stale/missing).
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

from shared.data_access import DataAccess, get_file_age_hours


def get_price_from_csv(ticker: str) -> Optional[Dict]:
    """
    Get latest price from CSV file.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with price, change, change_pct, date or None if not available
    """
    da = DataAccess()
    csv_path = da.get_price_csv(ticker)

    if not csv_path:
        return None

    try:
        import pandas as pd
        df = pd.read_csv(csv_path, parse_dates=["date"])

        if df.empty:
            return None

        # Normalize column names to lowercase for case-insensitive access
        df.columns = df.columns.str.lower()

        # Get last row
        last = df.iloc[-1]

        # Calculate change if possible
        change = None
        change_pct = None
        if len(df) >= 2:
            prev_close = df.iloc[-2]["close"]
            change = last["close"] - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0.0

        return {
            "price": float(last["close"]),
            "change": change,
            "change_pct": change_pct,
            "date": last["date"].strftime("%Y-%m-%d"),
            "source": "csv",
            "age_hours": get_file_age_hours(csv_path)
        }
    except Exception as e:
        print(f"Warning: Error reading CSV for {ticker}: {e}", file=sys.stderr)
        return None


def fetch_yfinance_price(ticker: str) -> Optional[Dict]:
    """
    Fetch current price from yfinance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with price, change, change_pct, date or None if failed
    """
    try:
        import yfinance as yf

        ticker_obj = yf.Ticker(ticker.upper())
        info = ticker_obj.info

        # Get current price
        price = info.get("currentPrice") or info.get("regularMarketPrice")

        if price is None:
            return None

        # Get previous close for change calculation
        prev_close = info.get("previousClose")

        change = None
        change_pct = None
        if prev_close and prev_close > 0:
            change = price - prev_close
            change_pct = (change / prev_close * 100)

        return {
            "price": float(price),
            "change": float(change) if change else None,
            "change_pct": float(change_pct) if change_pct else None,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "yfinance",
            "age_hours": 0.0  # Fresh from yfinance
        }
    except ImportError:
        print("Warning: yfinance not installed. Install with: pip install yfinance", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Error fetching from yfinance for {ticker}: {e}", file=sys.stderr)
        return None


def get_current_prices(tickers: List[str], force_refresh: bool = False) -> Dict[str, Dict]:
    """
    Get current prices for multiple tickers.

    Strategy:
    1. Try CSV first (if not force_refresh and fresh <24h)
    2. If stale or force_refresh, fetch from yfinance
    3. Fallback to CSV with staleness warning if yfinance fails

    Args:
        tickers: List of ticker symbols
        force_refresh: If True, skip CSV and use yfinance

    Returns:
        Dict mapping ticker to price data
    """
    results = {}

    for ticker in tickers:
        ticker_upper = ticker.upper()

        # Try CSV first (unless force_refresh)
        if not force_refresh:
            csv_data = get_price_from_csv(ticker_upper)
            if csv_data and csv_data["age_hours"] < 24:
                results[ticker_upper] = csv_data
                continue

        # Try yfinance
        yf_data = fetch_yfinance_price(ticker_upper)
        if yf_data:
            results[ticker_upper] = yf_data
            continue

        # Fallback to CSV with staleness warning
        if not force_refresh:
            csv_data = get_price_from_csv(ticker_upper)
            if csv_data:
                print(f"Warning: Using stale CSV data for {ticker_upper} ({csv_data['age_hours']:.1f}h old)", file=sys.stderr)
                results[ticker_upper] = csv_data
                continue

        # No price data available
        print(f"Warning: No price data available for {ticker_upper}", file=sys.stderr)
        results[ticker_upper] = {
            "price": None,
            "change": None,
            "change_pct": None,
            "date": None,
            "source": "N/A",
            "age_hours": float('inf')
        }

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch current prices for tickers")
    parser.add_argument("--tickers", type=str, required=True, help="Comma-separated list of tickers")
    parser.add_argument("--force-refresh", action="store_true", help="Force refresh from yfinance")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]

    results = get_current_prices(tickers, args.force_refresh)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
