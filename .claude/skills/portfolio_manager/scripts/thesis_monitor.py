#!/usr/bin/env python3
"""
Thesis monitoring script - alerts on thesis status changes.

Checks portfolio positions against key levels from investment thesis:
- Invalidations levels (bear case)
- Target prices (bull case)
- WARNING → DANGER transitions

Usage:
    python thesis_monitor.py [--portfolio NAME] [--alert-threshold LEVEL]
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Add shared module to path
# thesis_monitor.py is at .claude/skills/portfolio_manager/scripts/
# parents[0]=scripts, [1]=portfolio_manager, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.data_access"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from shared.data_access import DataAccess, get_project_root
    from shared.quality_scoring import score_analytics_files
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False

    def get_project_root() -> Path:
        """Fallback project root detection."""
        p = Path(__file__).resolve()
        markers = ['prices/', '.git/', 'watchlist.json']
        for parent in [p, *p.parents]:
            if any((parent / m).exists() for m in markers):
                return parent
        if ".claude" in p.parts:
            idx = p.parts.index(".claude")
            return Path(*p.parts[:idx])
        raise RuntimeError("Project root not found")

    class DataAccess:
        """Minimal fallback DataAccess."""
        def __init__(self):
            self.root = get_project_root()
            self.filedb_dir = self.root / "filedb"
            self._prices_dir = self.filedb_dir / "prices"
            self._analytics_dir = self.filedb_dir / "analytics"

        def read_price_data(self, ticker):
            import pandas as pd
            price_path = self._prices_dir / f"{ticker}.csv"
            if price_path.exists():
                df = pd.read_csv(price_path, index_col='date', parse_dates=True)
                return df
            return None

        def read_analytics(self, ticker):
            files = self.get_analytics_files(ticker)
            return {
                "technical": self._read_file(files.technical),
                "fundamental": self._read_file(files.fundamental),
                "thesis": self._read_file(files.thesis),
            }

        def get_analytics_files(self, ticker):
            analytics_dir = self.get_analytics_dir(ticker)
            from dataclasses import dataclass
            @dataclass
            class AnalyticsFiles:
                technical: Path
                fundamental: Path
                thesis: Path
            return AnalyticsFiles(
                technical=analytics_dir / f"{ticker}_technical_analysis.md",
                fundamental=analytics_dir / f"{ticker}_fundamental_analysis.md",
                thesis=analytics_dir / f"{ticker}_investment_thesis.md"
            )

        def get_analytics_dir(self, ticker):
            return self._analytics_dir / ticker

        def _read_file(self, path):
            if path and path.exists():
                return path.read_text()
            return None

        def get_portfolio(self, portfolio_name=None):
            import json
            portfolios_path = self.filedb_dir / "portfolios.json"
            if portfolios_path.exists():
                portfolios = json.load(open(portfolios_path))
                if portfolio_name is None:
                    portfolio_name = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
                return portfolios.get("portfolios", {}).get(portfolio_name, {"holdings": [], "summary": {}})
            return {"holdings": [], "summary": {}}

        def load_portfolios(self):
            import json
            portfolios_path = self.filedb_dir / "portfolios.json"
            if portfolios_path.exists():
                return json.load(open(portfolios_path))
            return {"portfolios": {}, "cash": {}}


# Thesis status levels
THESIS_LEVELS = {
    "DANGER": 1,      # Thesis broken / invalidation level breached
    "WARNING": 2,     # At risk / approaching invalidation
    "CAUTION": 3,     # Monitor closely
    "ON_TRACK": 4,    # Thesis progressing as expected
    "ACCELERATING": 5 # Ahead of schedule / upside surprise
}


def parse_thesis_levels(ticker: str, da: DataAccess) -> dict:
    """
    Parse key levels from investment thesis file.

    Args:
        ticker: Stock ticker symbol
        da: DataAccess instance

    Returns:
        Dict with invalidation_level, target_price, current_status
    """
    thesis_content = da.read_analytics(ticker).get("thesis", "")
    if not thesis_content:
        return {}

    levels = {}

    # Extract invalidation level (bear case)
    invalidation_patterns = [
        r'(?:invalidation|bear case|stop loss|downside).*?[\$]([0-9.]+)',
        r'(?:invalidation|bear case|stop loss|downside).*?([0-9.]+)\s*\.?\s*0',
    ]
    for pattern in invalidation_patterns:
        match = re.search(pattern, thesis_content, re.IGNORECASE | re.DOTALL)
        if match:
            levels["invalidation_level"] = float(match.group(1))
            break

    # Extract target price (bull case)
    target_patterns = [
        r'(?:target|price target|bull case|fair value).*?[\$]([0-9.]+)',
        r'(?:target|price target|bull case).*?([0-9.]+)\s*\.?\s*0',
    ]
    for pattern in target_patterns:
        match = re.search(pattern, thesis_content, re.IGNORECASE | re.DOTALL)
        if match:
            levels["target_price"] = float(match.group(1))
            break

    # Extract current thesis status
    status_patterns = [
        r'(?:thesis status|status)[:\s]+(DANGER|WARNING|CAUTION|ON_TRACK|ACCELERATING)',
        r'(?:THESIS_STATUS|THESIS)[:\s]+(DANGER|WARNING|CAUTION|ON_TRACK|ACCELERATING)',
    ]
    for pattern in status_patterns:
        match = re.search(pattern, thesis_content, re.IGNORECASE)
        if match:
            levels["current_status"] = match.group(1).upper()
            break

    # Default to ON_TRACK if not found
    if "current_status" not in levels:
        levels["current_status"] = "ON_TRACK"

    return levels


def get_current_price(ticker: str, da: DataAccess) -> float | None:
    """Get current price from price CSV or use last close."""
    df = da.read_price_data(ticker)
    if df is not None and not df.empty:
        return float(df['Close'].iloc[-1])
    return None


def assess_thesis_status(
    ticker: str,
    current_price: float,
    levels: dict
) -> dict:
    """
    Assess current thesis status based on price vs key levels.

    Args:
        ticker: Stock ticker symbol
        current_price: Current market price
        levels: Parsed key levels from thesis

    Returns:
        Dict with status, level, and reasoning
    """
    invalidation = levels.get("invalidation_level")
    target = levels.get("target_price")
    previous_status = levels.get("current_status", "ON_TRACK")

    # Calculate distance to key levels
    if invalidation and target:
        range_size = target - invalidation
        if range_size > 0:
            position = (current_price - invalidation) / range_size
        else:
            position = 0.5
    else:
        position = 0.5

    # Determine current status based on price position
    if invalidation and current_price <= invalidation * 1.05:
        current_status = "DANGER"
        reason = f"Price ${current_price:.2f} at/below invalidation level ${invalidation:.2f}"
    elif invalidation and current_price <= invalidation * 1.15:
        current_status = "WARNING"
        reason = f"Price ${current_price:.2f} within 15% of invalidation level ${invalidation:.2f}"
    elif target and current_price >= target * 0.95:
        current_status = "ACCELERATING"
        reason = f"Price ${current_price:.2f} at/near target ${target:.2f}"
    elif position >= 0.6:
        current_status = "ON_TRACK"
        reason = f"Price ${current_price:.2f} in upper range of thesis"
    else:
        current_status = "CAUTION"
        reason = f"Price ${current_price:.2f} in middle of thesis range"

    # Check for status transition (WARNING → DANGER is critical)
    previous_level = THESIS_LEVELS.get(previous_status, 3)
    current_level = THESIS_LEVELS.get(current_status, 3)
    transition = current_level - previous_level

    if transition <= -2:
        alert_level = "CRITICAL"
    elif transition == -1:
        alert_level = "WARNING"
    elif transition >= 1:
        alert_level = "POSITIVE"
    else:
        alert_level = "INFO"

    return {
        "ticker": ticker,
        "current_price": current_price,
        "status": current_status,
        "previous_status": previous_status,
        "alert_level": alert_level,
        "reason": reason,
        "levels": {
            "invalidation": invalidation,
            "target": target,
        },
        "transition": {
            "from": previous_status,
            "to": current_status,
            "change": transition
        }
    }


def monitor_portfolio_thesis(portfolio_name: str = None, da: DataAccess = None) -> dict:
    """
    Monitor thesis status for all portfolio holdings.

    Args:
        portfolio_name: Portfolio name (None for default)
        da: DataAccess instance

    Returns:
        Dict with alerts and summary
    """
    da = da or DataAccess()

    # Get portfolio
    if portfolio_name:
        portfolio = da.get_portfolio(portfolio_name)
    else:
        portfolios = da.load_portfolios()
        default_name = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
        portfolio = da.get_portfolio(default_name)
        portfolio_name = default_name

    holdings = portfolio.get("holdings", [])
    results = []
    alerts = []
    summary = {
        "total_holdings": len(holdings),
        "danger": 0,
        "warning": 0,
        "caution": 0,
        "on_track": 0,
        "accelerating": 0
    }

    for holding in holdings:
        ticker = holding.get("ticker")
        if not ticker:
            continue

        # Get current price
        current_price = holding.get("current_price") or get_current_price(ticker, da)
        if not current_price:
            continue

        # Parse thesis levels
        levels = parse_thesis_levels(ticker, da)
        if not levels:
            continue

        # Assess status
        status = assess_thesis_status(ticker, current_price, levels)
        results.append(status)

        # Count by status
        status_lower = status["status"].lower()
        summary[status_lower] = summary.get(status_lower, 0) + 1

        # Generate alerts for concerning transitions
        if status["alert_level"] in ("CRITICAL", "WARNING"):
            alerts.append({
                "ticker": ticker,
                "level": status["alert_level"],
                "transition": f"{status['previous_status']} → {status['status']}",
                "price": current_price,
                "reason": status["reason"],
                "timestamp": datetime.now().isoformat()
            })

    return {
        "portfolio": portfolio_name,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "holdings": results,
        "alerts": alerts,
        "alert_count": len(alerts)
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor thesis status for portfolio holdings",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--portfolio",
        type=str,
        help="Portfolio name (default: CORE)"
    )
    parser.add_argument(
        "--alert-threshold",
        choices=["INFO", "WARNING", "CRITICAL"],
        default="WARNING",
        help="Minimum alert level to display (default: WARNING)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    da = DataAccess() if SHARED_AVAILABLE else None
    if not SHARED_AVAILABLE:
        # Initialize basic DataAccess fallback
        from data_access import DataAccess
        da = DataAccess()

    result = monitor_portfolio_thesis(args.portfolio, da)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"THESIS MONITOR: {result['portfolio']}")
        print(f"{'='*60}")
        print(f"Checked: {result['summary']['total_holdings']} holdings")
        print(f"Time: {result['timestamp']}")

        print(f"\nStatus Summary:")
        for status, count in result['summary'].items():
            if status != "total_holdings" and count > 0:
                print(f"  {status.upper()}: {count}")

        if result['alerts']:
            threshold_order = ["CRITICAL", "WARNING", "POSITIVE", "INFO"]
            threshold_idx = threshold_order.index(args.alert_threshold)

            print(f"\n{'='*60}")
            print(f"ALERTS (>= {args.alert_threshold}):")
            print(f"{'='*60}")

            for alert in result['alerts']:
                alert_idx = threshold_order.index(alert['level'])
                if alert_idx >= threshold_idx:
                    icon = {"CRITICAL": "🚨", "WARNING": "⚠️", "POSITIVE": "✅", "INFO": "ℹ️"}[alert['level']]
                    print(f"{icon} {alert['ticker']}: {alert['transition']}")
                    print(f"   Price: ${alert['price']:.2f}")
                    print(f"   Reason: {alert['reason']}")
                    print()

        # Show detailed holdings
        print(f"\nDetailed Status:")
        for holding in result['holdings']:
            ticker = holding['ticker']
            status = holding['status']
            price = holding['current_price']
            prev = holding['previous_status']
            icon = {"DANGER": "🔴", "WARNING": "🟡", "CAUTION": "🟠", "ON_TRACK": "🟢", "ACCELERATING": "🚀"}[status]
            transition = f" ({prev} → {status})" if prev != status else ""
            print(f"  {icon} {ticker}: ${price:.2f} [{status}]{transition}")

    # Exit with error if CRITICAL alerts
    critical_count = sum(1 for a in result['alerts'] if a['level'] == 'CRITICAL')
    if critical_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
