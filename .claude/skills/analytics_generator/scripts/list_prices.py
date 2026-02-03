#!/usr/bin/env python3
"""
List all available price files in the prices/ directory.

Usage:
    python list_prices.py
"""
import json
import sys
from pathlib import Path

# Add shared module to path
# list_prices.py is at .claude/skills/analytics_generator/scripts/
# parents[0]=scripts, [1]=analytics_generator, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.data_access"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

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


def list_price_files() -> dict:
    """
    List all price files in the prices/ directory.

    Returns:
        Dictionary with list of available tickers and metadata
    """
    project_root = get_project_root()
    prices_dir = project_root / 'prices'

    if not prices_dir.exists():
        return {
            'status': 'success',
            'count': 0,
            'tickers': []
        }

    try:
        import pandas as pd

        price_files = list(prices_dir.glob('*.csv'))
        tickers = []

        for csv_path in sorted(price_files):
            ticker = csv_path.stem  # Filename without .csv

            try:
                df = pd.read_csv(csv_path, index_col='date', parse_dates=True)

                tickers.append({
                    'ticker': ticker.upper(),
                    'file': str(csv_path.relative_to(project_root)),
                    'data_points': len(df),
                    'start_date': df.index[0].strftime('%Y-%m-%d') if not df.empty else None,
                    'end_date': df.index[-1].strftime('%Y-%m-%d') if not df.empty else None,
                    'latest_price': round(float(df['Close'].iloc[-1]), 4) if not df.empty else None
                })
            except Exception as e:
                tickers.append({
                    'ticker': ticker.upper(),
                    'file': str(csv_path.relative_to(project_root)),
                    'error': str(e)
                })

        return {
            'status': 'success',
            'count': len(tickers),
            'tickers': tickers
        }

    except ImportError:
        # If pandas not available, just list files
        price_files = list(prices_dir.glob('*.csv'))
        tickers = [
            {
                'ticker': f.stem.upper(),
                'file': str(f.relative_to(project_root))
            }
            for f in sorted(price_files)
        ]

        return {
            'status': 'success',
            'count': len(tickers),
            'tickers': tickers
        }


def main():
    """Main entry point."""
    result = list_price_files()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
