#!/usr/bin/env python3
"""
Batch analyze multiple tickers - create/update analytics files.

Integrates batch_create_analytics and batch_classify functionality.

Usage:
    python batch_analyze.py all
    python batch_analyze.py core
    python batch_analyze.py NVDA,AAPL,MSFT
    python batch_analyze.py moonshots --parallel
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Add shared module to path
# batch_analyze.py is at .claude/skills/watchlist_manager/scripts/
# parents[0]=scripts, [1]=watchlist_manager, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.data_access"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from shared.data_access import DataAccess, get_file_age_hours
    from shared.quality_scoring import score_analytics_files
    from shared.parallel_fetch import fetch_all_data
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    # Fallback - define minimal implementations inline
    def get_file_age_hours(filepath):
        from datetime import datetime
        if not filepath.exists():
            return float('inf')
        mtime = filepath.stat().st_mtime
        age_seconds = datetime.now().timestamp() - mtime
        return age_seconds / 3600

    def get_project_root():
        current = Path(__file__).resolve()
        markers = ['.git', 'watchlist.json', 'prices/', 'analytics/']
        for parent in [current, *current.parents]:
            if any((parent / m).exists() for m in markers):
                return parent
        if ".claude" in current.parts:
            idx = current.parts.index(".claude")
            return Path(*current.parts[:idx])
        raise RuntimeError("Project root not found")

    class DataAccess:
        def __init__(self):
            self.root = get_project_root()
            self._prices_dir = self.root / "prices"
            self._analytics_dir = self.root / "analytics"

        def load_watchlist(self):
            import json
            path = self.root / "watchlist.json"
            if path.exists():
                return json.load(open(path))
            return {"tickers": {}}

        def get_analytics_dir(self, ticker):
            return self._analytics_dir / ticker

        def get_analytics_files(self, ticker):
            from dataclasses import dataclass
            @dataclass
            class AnalyticsFiles:
                technical: Path
                fundamental: Path
                thesis: Path
                exists: bool
            d = self.get_analytics_dir(ticker)
            return AnalyticsFiles(
                technical=d / f"{ticker}_technical_analysis.md",
                fundamental=d / f"{ticker}_fundamental_analysis.md",
                thesis=d / f"{ticker}_investment_thesis.md",
                exists=d.exists()
            )

        def read_price_data(self, ticker):
            import pandas as pd
            path = self._prices_dir / f"{ticker}.csv"
            if path.exists():
                return pd.read_csv(path, index_col='date', parse_dates=True)
            return None

        def read_analytics(self, ticker):
            files = self.get_analytics_files(ticker)
            return {
                "technical": self._read_file(files.technical),
                "fundamental": self._read_file(files.fundamental),
                "thesis": self._read_file(files.thesis),
            }

        def _read_file(self, path):
            if path and path.exists():
                return path.read_text()
            return None

    def score_analytics_files(ticker, max_age_hours=24):
        from dataclasses import dataclass
        @dataclass
        class QualityScore:
            overall: int
            freshness: int
            completeness: int
            accuracy: int
            breakdown: dict
            action: str
        return QualityScore(
            overall=50, freshness=50, completeness=50, accuracy=50,
            breakdown={}, action="REFRESH_REQUIRED"
        )

    def fetch_all_data(ticker, data_access=None):
        return {"analytics": {}, "prices": None, "news_files": [], "quality": {}}

try:
    import yfinance as yf
    import pandas as pd
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


def get_tickers_for_segment(segment: str, da: DataAccess) -> list:
    """
    Get tickers for a given segment.

    Args:
        segment: Segment name (all, core, moonshots, or comma-separated tickers)
        da: DataAccess instance

    Returns:
        List of ticker symbols
    """
    # Check if it's a comma-separated list of tickers
    if ',' in segment or segment.isalpha() and len(segment) <= 6:
        # Could be a single ticker or comma-separated list
        if ',' in segment:
            return [t.strip().upper() for t in segment.split(',')]
        # Check if it exists in watchlist
        watchlist = da.load_watchlist()
        if segment.upper() in watchlist.get("tickers", {}):
            return [segment.upper()]

    # Load watchlist
    watchlist = da.load_watchlist()
    all_tickers = list(watchlist.get("tickers", {}).keys())

    segment_lower = segment.lower()

    if segment_lower == "all":
        return all_tickers
    elif segment_lower == "core":
        # Filter for compounder types
        return [
            t for t, data in watchlist.get("tickers", {}).items()
            if data.get("investment_type") == "compounder"
        ]
    elif segment_lower == "moonshots":
        # Filter for moonshot types
        return [
            t for t, data in watchlist.get("tickers", {}).items()
            if data.get("investment_type") == "moonshot"
        ]
    else:
        # Try as single ticker
        if segment_upper in all_tickers:
            return [segment.upper()]
        return []


def analyze_single_ticker(ticker: str, da: DataAccess, force_refresh: bool = False) -> dict:
    """
    Analyze a single ticker - create or update analytics files.

    Args:
        ticker: Stock ticker symbol
        da: DataAccess instance
        force_refresh: Force refresh even if data is fresh

    Returns:
        Dict with analysis results
    """
    ticker = ticker.upper()
    files = da.get_analytics_files(ticker)

    result = {
        "ticker": ticker,
        "timestamp": datetime.now().isoformat(),
        "actions": [],
        "quality": {},
        "errors": [],
    }

    # Check freshness of existing analytics
    if not force_refresh and files.exists():
        max_age_hours = 24
        ages = {}
        all_fresh = True

        for file_type in ["technical", "fundamental", "thesis"]:
            filepath = getattr(files, file_type)
            if filepath and filepath.exists():
                age = get_file_age_hours(filepath)
                ages[file_type] = round(age, 1)
                if age > max_age_hours:
                    all_fresh = False
            else:
                all_fresh = False

        if all_fresh:
            result["actions"].append("already_fresh")
            result["quality"] = {
                "ages": ages,
                "status": "fresh"
            }
            return result

    # Need to fetch/update data
    try:
        if not HAS_YFINANCE:
            result["errors"].append("yfinance not available")
            return result

        # Fetch price data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")

        if hist.empty:
            result["errors"].append(f"No data for {ticker}")
            return result

        # Save price data
        prices_dir = da.root / "prices"
        prices_dir.mkdir(exist_ok=True)
        price_path = prices_dir / f"{ticker}.csv"

        # Append mode: check for existing file
        if price_path.exists():
            existing_df = pd.read_csv(price_path, index_col='date', parse_dates=True)
            if not existing_df.empty:
                last_date = existing_df.index[-1]
                new_hist = hist[hist.index > last_date]
                if not new_hist.empty:
                    new_hist.index.name = 'date'
                    new_hist.to_csv(price_path, mode='a', header=False)
                    result["actions"].append(f"appended_{len(new_hist)}_price_days")
                else:
                    result["actions"].append("price_current")
            else:
                hist.index.name = 'date'
                hist.to_csv(price_path)
                result["actions"].append(f"created_price_file_{len(hist)}_days")
        else:
            hist.index.name = 'date'
            hist.to_csv(price_path)
            result["actions"].append(f"created_price_file_{len(hist)}_days")

        result["actions"].append("price_fetched")

        # Check analytics directory
        analytics_dir = da.get_analytics_dir(ticker)
        analytics_dir.mkdir(parents=True, exist_ok=True)

        # Mark for LLM analysis
        result["actions"].append("analytics_ready_for_llm")
        result["status"] = "needs_llm_generation"

    except Exception as e:
        result["errors"].append(str(e))

    return result


def batch_analyze(
    segment: str,
    parallel: bool = False,
    force_refresh: bool = False,
    da: DataAccess = None
) -> dict:
    """
    Batch analyze multiple tickers.

    Args:
        segment: Segment name or tickers
        parallel: Use parallel execution
        force_refresh: Force refresh even if data is fresh
        da: DataAccess instance

    Returns:
        Summary dict with results for all tickers
    """
    da = da or DataAccess()

    # Get tickers for segment
    tickers = get_tickers_for_segment(segment, da)

    if not tickers:
        return {
            "segment": segment,
            "error": "No tickers found for segment",
            "timestamp": datetime.now().isoformat()
        }

    results = {}
    errors = []
    created = 0
    updated = 0
    fresh = 0

    if parallel and len(tickers) > 1:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(analyze_single_ticker, ticker, da, force_refresh): ticker
                for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    results[ticker] = result

                    if "already_fresh" in result.get("actions", []):
                        fresh += 1
                    elif "price_fetched" in result.get("actions", []):
                        if "created" in str(result.get("actions", [])):
                            created += 1
                        else:
                            updated += 1

                    if result.get("errors"):
                        errors.extend([f"{ticker}: {e}" for e in result["errors"]])

                except Exception as e:
                    errors.append(f"{ticker}: {str(e)}")
                    results[ticker] = {"ticker": ticker, "errors": [str(e)]}
    else:
        # Sequential execution
        for ticker in tickers:
            result = analyze_single_ticker(ticker, da, force_refresh)
            results[ticker] = result

            if "already_fresh" in result.get("actions", []):
                fresh += 1
            elif "price_fetched" in result.get("actions", []):
                if "created" in str(result.get("actions", [])):
                    created += 1
                else:
                    updated += 1

            if result.get("errors"):
                errors.extend([f"{ticker}: {e}" for e in result["errors"]])

    return {
        "segment": segment,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(tickers),
            "fresh": fresh,
            "created": created,
            "updated": updated,
            "errors": len(errors)
        },
        "tickers": list(tickers),
        "results": results,
        "all_errors": errors
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch analyze tickers - create/update analytics files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_analyze.py all
  python batch_analyze.py core
  python batch_analyze.py moonshots --parallel
  python batch_analyze.py NVDA,AAPL,MSFT
        """
    )
    parser.add_argument("segment", help="Segment name or comma-separated tickers")
    parser.add_argument("--parallel", action="store_true", help="Run in parallel")
    parser.add_argument("--force", action="store_true", help="Force refresh even if fresh")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    da = DataAccess()
    result = batch_analyze(args.segment, args.parallel, args.force, da)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f" BATCH ANALYZE: {result['segment'].upper()}")
        print(f"{'='*60}")
        print(f"Time: {result['timestamp']}")

        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

        summary = result.get("summary", {})
        print(f"\nSummary:")
        print(f"  Total tickers: {summary.get('total', 0)}")
        print(f"  Already fresh: {summary.get('fresh', 0)}")
        print(f"  Created: {summary.get('created', 0)}")
        print(f"  Updated: {summary.get('updated', 0)}")
        print(f"  Errors: {summary.get('errors', 0)}")

        if result.get("all_errors"):
            print(f"\nErrors:")
            for error in result["all_errors"]:
                print(f"  - {error}")

        print(f"\nResults:")
        for ticker, res in result.get("results", {}).items():
            actions = res.get("actions", [])
            errs = res.get("errors", [])
            status_icon = "✓" if not errs else "✗"
            actions_str = ", ".join(actions) if actions else "analyzed"
            print(f"  {status_icon} {ticker}: {actions_str}")
            if errs:
                for err in errs:
                    print(f"      ERROR: {err}")


if __name__ == "__main__":
    main()
