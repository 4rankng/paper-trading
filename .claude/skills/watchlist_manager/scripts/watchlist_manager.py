#!/usr/bin/env python3
"""
Watchlist Manager - Lean Schema

Concise watchlist for quick scanning.
For deep analysis, use analytics_generator or trading-plan skills.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add script directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Import strategy classifier
try:
    from strategy_classifier import classify, STRATEGIES
except ImportError:
    classify = None
    STRATEGIES = {}


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(*current_path.parts[:current_path.parts.index("skills") - 2])


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _parse_nullable(value: Optional[str]) -> Optional[str]:
    """Parse command line argument, treating 'null' as None."""
    if value is None or value.lower() == "null":
        return None
    return value


def output_success(data: dict) -> None:
    """Output success JSON."""
    data['status'] = 'success'
    data['timestamp'] = get_timestamp()
    print(json.dumps(data, indent=2))


def output_error(message: str, exit_code: int = 1) -> None:
    """Output error JSON and exit."""
    print(json.dumps({
        'status': 'error',
        'error': message,
        'timestamp': get_timestamp()
    }, indent=2))
    sys.exit(exit_code)


# ============================================================================
# FILE OPERATIONS
# ============================================================================

class WatchlistManager:
    """Manages lean watchlist.json."""

    def __init__(self, watchlist_path: Path = None):
        """Initialize WatchlistManager."""
        project_root = get_project_root()
        self.watchlist_path = watchlist_path or (project_root / "watchlist.json")
        self._watchlist_cache = None

    def _load_watchlist(self) -> List[Dict]:
        """Load watchlist from file."""
        if self._watchlist_cache is None:
            if not self.watchlist_path.exists():
                self._watchlist_cache = []
            else:
                with open(self.watchlist_path, 'r', encoding='utf-8') as f:
                    self._watchlist_cache = json.load(f)
        return self._watchlist_cache

    def _save_watchlist(self, watchlist: List[Dict]) -> None:
        """Save watchlist to file."""
        with open(self.watchlist_path, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, indent=2, ensure_ascii=False)
        self._watchlist_cache = watchlist

    def _normalize_stock_entry(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize stock entry: convert unclassified/unknown to null, enforce fit rules."""
        # Convert "unclassified" and "unknown" to null
        if stock.get("strategy") in ("unclassified", "unknown", ""):
            stock["strategy"] = None
        if stock.get("hold") in ("unknown", "", "unclassified"):
            stock["hold"] = None

        # If strategy is null, remove trading-related fields (fit, exit, stop, rr)
        if stock.get("strategy") is None:
            stock.pop("fit", None)
            stock.pop("exit", None)
            stock.pop("stop", None)
            stock.pop("rr", None)

        return stock

    def find_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Find stock by ticker."""
        watchlist = self._load_watchlist()
        ticker_upper = ticker.upper()
        for stock in watchlist:
            if stock.get("ticker", "").upper() == ticker_upper:
                return stock
        return None

    def search(self, filters: Dict[str, Any], limit: int = None, sort: str = None) -> List[Dict]:
        """Search watchlist with filters."""
        watchlist = self._load_watchlist()
        results = []

        for stock in watchlist:
            match = True

            # Ticker filter
            if "ticker" in filters:
                if stock.get("ticker", "").upper() != filters["ticker"].upper():
                    match = False

            # Multiple tickers
            if "tickers" in filters:
                tickers_upper = [t.upper() for t in filters["tickers"]]
                if stock.get("ticker", "").upper() not in tickers_upper:
                    match = False

            # Name filter
            if "name" in filters:
                if filters["name"].lower() not in stock.get("name", "").lower():
                    match = False

            # Sector filter
            if "sector" in filters:
                if filters["sector"].lower() not in stock.get("sector", "").lower():
                    match = False

            # Action filter
            if "action" in filters:
                if filters["action"].upper() != stock.get("action", "").upper():
                    match = False

            # Strategy filter
            if "strategy" in filters:
                if filters["strategy"].lower() != stock.get("strategy", "").lower():
                    match = False

            # Holding period filter
            if "holding_period" in filters:
                if filters["holding_period"].lower() not in stock.get("hold", "").lower():
                    match = False

            # Min fit filter
            if "min_fit" in filters:
                if stock.get("fit", 0) < filters["min_fit"]:
                    match = False

            # Min price filter
            if "min_price" in filters:
                price = stock.get("price")
                if price is None or price < filters["min_price"]:
                    match = False

            # Max price filter
            if "max_price" in filters:
                price = stock.get("price")
                if price is None or price > filters["max_price"]:
                    match = False

            # Min RR filter
            if "min_rr" in filters:
                rr = stock.get("rr")
                if rr is None or rr < filters["min_rr"]:
                    match = False

            if match:
                results.append(stock.copy())

        # Sort results
        if sort:
            results = self._sort_results(results, sort)

        if limit and limit > 0:
            results = results[:limit]

        return results

    def _sort_results(self, results: List[Dict], sort: str) -> List[Dict]:
        """Sort results."""
        if sort == "ticker":
            results.sort(key=lambda x: x.get("ticker", ""))
        elif sort == "fit" or sort == "score":
            results.sort(key=lambda x: x.get("fit", 0), reverse=True)
        elif sort == "rr" or sort == "risk_reward":
            results.sort(key=lambda x: x.get("rr", 0), reverse=True)
        elif sort == "price":
            results.sort(key=lambda x: x.get("price", 0), reverse=True)
        return results

    def add_stock(self, stock_data: Dict[str, Any]) -> Dict:
        """Add new stock to watchlist."""
        # Validate required fields
        required = ["ticker", "name", "sector"]
        missing = [f for f in required if not stock_data.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        ticker = stock_data["ticker"].upper()

        # Check duplicates
        if self.find_by_ticker(ticker):
            raise ValueError(f"Ticker {ticker} already exists")

        # Create lean entry (LLM agent provides strategy/hold/fit from analytics)
        new_stock = {
            "ticker": ticker,
            "name": stock_data["name"],
            "sector": stock_data["sector"],
            "strategy": stock_data.get("strategy"),
            "hold": stock_data.get("hold"),
            "action": stock_data.get("action", "WATCH").upper(),
            "updated_at": get_today_date(),
        }

        # Only add fit if provided
        if stock_data.get("fit") is not None:
            new_stock["fit"] = stock_data["fit"]

        # Optional fields
        if stock_data.get("price") is not None:
            new_stock["price"] = stock_data["price"]
        if stock_data.get("exit") is not None:
            new_stock["exit"] = stock_data["exit"]
        if stock_data.get("stop") is not None:
            new_stock["stop"] = stock_data["stop"]

        # Calculate RR if we have price, exit, stop
        if "price" in new_stock and "exit" in new_stock and "stop" in new_stock:
            price = new_stock["price"]
            upside = ((new_stock["exit"] - price) / price) * 100
            downside = ((price - new_stock["stop"]) / price) * 100
            new_stock["rr"] = round(upside / downside, 2) if downside > 0 else 0

        # Normalize entry (converts unclassified/unknown to null, removes irrelevant fields)
        new_stock = self._normalize_stock_entry(new_stock)

        watchlist = self._load_watchlist()
        watchlist.append(new_stock)
        self._save_watchlist(watchlist)

        return new_stock

    def update_stock(self, ticker: str, updates: Dict[str, Any]) -> Dict:
        """Update existing stock."""
        watchlist = self._load_watchlist()
        ticker_upper = ticker.upper()

        for i, stock in enumerate(watchlist):
            if stock.get("ticker", "").upper() == ticker_upper:
                # Apply updates
                for key, value in updates.items():
                    watchlist[i][key] = value

                # Update timestamp
                watchlist[i]["updated_at"] = get_today_date()

                # Recalculate RR if price/exit/stop changed
                if "price" in updates or "exit" in updates or "stop" in updates:
                    s = watchlist[i]
                    if "price" in s and "exit" in s and "stop" in s:
                        price = s["price"]
                        if price and s["exit"] and s["stop"]:
                            upside = ((s["exit"] - price) / price) * 100
                            downside = ((price - s["stop"]) / price) * 100
                            s["rr"] = round(upside / downside, 2)

                # Normalize entry (converts unclassified/unknown to null, removes irrelevant fields)
                watchlist[i] = self._normalize_stock_entry(watchlist[i])

                self._save_watchlist(watchlist)
                return watchlist[i]

        raise ValueError(f"Ticker {ticker} not found")

    def remove_stock(self, ticker: str) -> Dict:
        """Remove stock from watchlist."""
        watchlist = self._load_watchlist()
        ticker_upper = ticker.upper()

        for i, stock in enumerate(watchlist):
            if stock.get("ticker", "").upper() == ticker_upper:
                removed = watchlist.pop(i)
                self._save_watchlist(watchlist)
                return removed

        raise ValueError(f"Ticker {ticker} not found")

    def get_summary(self) -> Dict[str, Any]:
        """Get watchlist summary."""
        watchlist = self._load_watchlist()

        summary = {
            "total_stocks": len(watchlist),
            "by_sector": {},
            "by_action": {},
            "by_strategy": {},
            "by_hold": {},
            "avg_fit": 0,
            "classified_count": 0
        }

        total_fit = 0
        fit_count = 0

        for stock in watchlist:
            sector = stock.get("sector", "Unknown")
            summary["by_sector"][sector] = summary["by_sector"].get(sector, 0) + 1

            action = stock.get("action", "Unknown")
            summary["by_action"][action] = summary["by_action"].get(action, 0) + 1

            strategy = stock.get("strategy")
            if strategy:
                summary["by_strategy"][strategy] = summary["by_strategy"].get(strategy, 0) + 1
                summary["classified_count"] += 1
            else:
                summary["by_strategy"]["unclassified"] = summary["by_strategy"].get("unclassified", 0) + 1

            hold = stock.get("hold")
            if hold:
                summary["by_hold"][hold] = summary["by_hold"].get(hold, 0) + 1
            else:
                summary["by_hold"]["unclassified"] = summary["by_hold"].get("unclassified", 0) + 1

            if stock.get("fit") is not None:
                total_fit += stock["fit"]
                fit_count += 1

        if fit_count > 0:
            summary["avg_fit"] = round(total_fit / fit_count, 1)

        return summary


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_compact(results: List[Dict]) -> str:
    """Format results as compact table."""
    if not results:
        return "No matching stocks found."

    output = [f"# Watchlist ({len(results)} stocks)"]
    output.append("")
    output.append(f"{'Ticker':<6} {'Strategy':<16} {'Hold':<8} {'Fit':<4} {'Action':<8} {'Price':<10} {'Updated':<10}")
    output.append("-" * 80)

    for stock in results:
        ticker = stock.get("ticker", "N/A")
        strategy = stock.get("strategy") or "-"
        hold = stock.get("hold") or "-"
        fit = stock.get("fit")
        action = stock.get("action", "N/A")
        price = stock.get("price")
        updated = stock.get("updated_at", "N/A")

        fit_str = f"{fit}" if fit is not None else "-"
        price_str = f"${price:.2f}" if price else "N/A"

        output.append(f"{ticker:<6} {strategy:<16} {hold:<8} {fit_str:<4} {action:<8} {price_str:<10} {updated:<10}")

    return "\n".join(output)


def format_summary_human(summary: Dict) -> str:
    """Format summary as human-readable text."""
    output = ["Watchlist Summary", "=" * 40]
    output.append(f"Total: {summary['total_stocks']} | Avg Fit: {summary.get('avg_fit', 0)}")

    output.append("\nBy Sector:")
    for sector, count in sorted(summary['by_sector'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {sector}: {count}")

    output.append("\nBy Action:")
    for action, count in sorted(summary['by_action'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {action}: {count}")

    output.append("\nBy Strategy:")
    for strategy, count in sorted(summary['by_strategy'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {strategy}: {count}")

    output.append("\nBy Hold Period:")
    for hold, count in sorted(summary['by_hold'].items()):
        output.append(f"  {hold}: {count}")

    return "\n".join(output)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manage watchlist.json - Lean Schema with Strategy Classification'
    )

    # Modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--add', action='store_true')
    mode_group.add_argument('--update', action='store_true')
    mode_group.add_argument('--remove', action='store_true')
    mode_group.add_argument('--summary', action='store_true')

    # Filters
    parser.add_argument('--ticker', help='Search by ticker')
    parser.add_argument('--tickers', help='Batch search by comma-separated tickers')
    parser.add_argument('--sector', help='Filter by sector')
    parser.add_argument('--action', help='Filter by action')
    parser.add_argument('--filter-strategy', dest='filter_strategy', help='Filter by strategy')
    parser.add_argument('--holding-period', dest='holding_period', help='Filter by holding period')
    parser.add_argument('--min-fit', type=int, help='Minimum fit score')
    parser.add_argument('--min-price', type=float, help='Minimum price')
    parser.add_argument('--max-price', type=float, help='Maximum price')
    parser.add_argument('--min-rr', type=float, help='Minimum risk/reward ratio')
    parser.add_argument('--top', type=int, help='Limit results')
    parser.add_argument('--sort', choices=['ticker', 'fit', 'rr', 'price'], help='Sort results')

    # Add/Update fields
    parser.add_argument('--name', help='Stock name (required for --add)')
    parser.add_argument('--strategy', help='Strategy classification (determined by LLM from analytics)')
    parser.add_argument('--hold', help='Holding period (1-10d, 2w-3m, 3-6m, 1y+)')
    parser.add_argument('--fit', type=int, help='Strategy fit score (0-100, determined by LLM)')
    parser.add_argument('--add-action', dest='add_action', choices=['BUY', 'SELL', 'WATCH', 'AVOID'],
                        help='Action signal for --add/--update')
    parser.add_argument('--price', type=float, help='Current price')
    parser.add_argument('--exit', type=float, help='Target exit price')
    parser.add_argument('--stop', type=float, help='Stop loss price')

    # Output
    parser.add_argument('--format', choices=['json', 'compact', 'human'], default='json')

    args = parser.parse_args()
    manager = WatchlistManager()

    # Summary mode
    if args.summary:
        summary = manager.get_summary()
        if args.format == 'human':
            print(format_summary_human(summary))
        else:
            output_success({"summary": summary})
        return

    # Add mode
    if args.add:
        if not args.name or not args.ticker or not args.sector:
            output_error("MISSING_REQUIRED", "--name, --ticker, --sector required for --add")

        stock_data = {
            "ticker": args.ticker,
            "name": args.name,
            "sector": args.sector,
            "strategy": _parse_nullable(args.strategy),
            "hold": _parse_nullable(args.hold),
            "fit": args.fit,
            "action": args.add_action or "WATCH",
            "price": args.price,
            "exit": args.exit,
            "stop": args.stop
        }

        result = manager.add_stock(stock_data)
        output_success({"action": "added", "stock": result})
        return

    # Update mode
    if args.update:
        if not args.ticker:
            output_error("MISSING_TICKER", "--ticker required for --update")

        updates = {}
        if args.price is not None:
            updates["price"] = args.price
        if args.exit is not None:
            updates["exit"] = args.exit
        if args.stop is not None:
            updates["stop"] = args.stop
        if args.add_action:
            updates["strategy"] = _parse_nullable(args.strategy)
            updates["hold"] = _parse_nullable(args.hold)
            updates["action"] = args.add_action
        elif args.strategy:
            updates["strategy"] = _parse_nullable(args.strategy)
        if args.hold:
            updates["hold"] = _parse_nullable(args.hold)
        if args.fit is not None:
            updates["fit"] = args.fit

        if not updates:
            output_error("NO_UPDATES", "No fields to update")

        result = manager.update_stock(args.ticker, updates)
        output_success({"action": "updated", "stock": result})
        return

    # Remove mode
    if args.remove:
        if not args.ticker:
            output_error("MISSING_TICKER", "--ticker required for --remove")
        result = manager.remove_stock(args.ticker)
        output_success({"action": "removed", "stock": result})
        return

    # Search mode (default)
    filters = {}
    if args.ticker:
        filters["ticker"] = args.ticker
    elif args.tickers:
        filters["tickers"] = [t.strip() for t in args.tickers.split(",")]
    if args.sector:
        filters["sector"] = args.sector
    if args.action:
        filters["action"] = args.action
    if args.filter_strategy:
        filters["strategy"] = args.filter_strategy
    if args.holding_period:
        filters["holding_period"] = args.holding_period
    if args.min_fit:
        filters["min_fit"] = args.min_fit
    if args.min_price:
        filters["min_price"] = args.min_price
    if args.max_price:
        filters["max_price"] = args.max_price
    if args.min_rr:
        filters["min_rr"] = args.min_rr

    results = manager.search(filters, limit=args.top, sort=args.sort)

    if args.format == 'compact':
        print(format_compact(results))
    elif args.format == 'human':
        print(format_compact(results))  # Same for now
    else:
        output_success({"results": results, "total_count": len(results)})


if __name__ == "__main__":
    main()
