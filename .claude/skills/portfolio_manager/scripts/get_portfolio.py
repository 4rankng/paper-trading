#!/usr/bin/env python3
"""
Get current portfolio status and holdings (v3.0 Minimal).

Usage:
    python get_portfolio.py
    python get_portfolio.py --portfolio CORE
    python get_portfolio.py --list
    python get_portfolio.py --format human

Note (v3.0): portfolios.json only stores minimal data.
              Analysis data is in analytics/[TICKER]/ folder - read separately if needed.
"""
import argparse
import json
import sys
from pathlib import Path

from common import (
    get_project_root,
    get_filedb_dir,
    get_portfolio,
    get_shared_cash,
    list_portfolios,
    format_currency,
    format_percent
)


def simplify_holding(h: dict, shared_cash: float = 0, total_value: float = 0) -> dict:
    """Extract only essential fields for LLM consumption (v3.0 minimal schema)."""
    shares = h.get("shares", 0)
    avg_cost = h.get("avg_cost", 0)
    current_price = h.get("current_price", avg_cost)

    market_value = shares * current_price
    cost_basis = shares * avg_cost
    gain_loss = market_value - cost_basis
    gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
    pct_portfolio = (market_value / total_value * 100) if total_value > 0 else 0

    return {
        "ticker": h.get("ticker"),
        "shares": shares,
        "avg_cost": avg_cost,
        "current_price": current_price,
        "market_value": round(market_value, 2),
        "gain_loss": round(gain_loss, 2),
        "gain_loss_pct": round(gain_loss_pct, 2),
        "pct_portfolio": round(pct_portfolio, 2),
        "status": h.get("status", "active"),
    }


def get_portfolio_status(portfolio_name: str | None = None, verbose: bool = False) -> dict:
    """Get current portfolio status.

    Args:
        portfolio_name: Name of portfolio (e.g., "CORE", "AI_PICKS"). If None, uses default.
        verbose: If True, return full holding data. Otherwise, simplified for LLM.
    """
    try:
        portfolios_path = get_filedb_dir() / "portfolios.json"

        if not portfolios_path.exists():
            return {"status": "error", "error": f"Portfolios file not found: {portfolios_path}"}

        portfolio = get_portfolio(portfolio_name)
        holdings = portfolio.get("holdings", [])
        shared_cash = get_shared_cash(portfolios_path)
        cash_amount = shared_cash.get("amount", 0)

        # Calculate total value for position percentages
        holdings_value = sum(
            h.get("shares", 0) * h.get("current_price", h.get("avg_cost", 0))
            for h in holdings
        )
        total_value = holdings_value + cash_amount

        return {
            "status": "success",
            "portfolio": portfolio_name or "default",
            "timestamp": str(Path(__file__).stat().st_mtime),  # File mtime as timestamp
            "shared_cash": shared_cash,
            "cash": shared_cash,  # For backward compatibility
            "holdings_count": len(holdings),
            "holdings": holdings if verbose else [
                simplify_holding(h, cash_amount, total_value) for h in holdings
            ],
            "summary": portfolio.get("summary", {}),
            "description": portfolio.get("description", ""),
        }
    except ValueError as e:
        return {"status": "error", "error": str(e)}
    except FileNotFoundError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def format_human_readable(result: dict, portfolio_name: str = None) -> str:
    """Format portfolio status as human-readable text."""
    if result["status"] == "error":
        return f"Error: {result['error']}"

    # Get actual portfolio name and description
    root = get_project_root()
    if portfolio_name is None:
        try:
            with open(root / "portfolios.json") as f:
                portfolios = json.load(f)
                portfolio_name = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
        except:
            portfolio_name = "UNKNOWN"

    try:
        with open(root / "portfolios.json") as f:
            portfolios = json.load(f)
            description = portfolios.get("portfolios", {}).get(portfolio_name, {}).get("description", "")
    except:
        description = ""

    cash = result.get("cash", result.get("shared_cash", {}))
    shared_cash = result.get("shared_cash", cash)

    output = [
        f"Portfolio: {portfolio_name}",
    ]
    if description:
        output.append(f"Description: {description}")

    output.extend([
        "=" * 60,
        f"Shared Cash: {format_currency(shared_cash.get('amount', 0))} (Target Buffer: {shared_cash.get('target_buffer_pct', 15)}%)",
        f"\nHoldings ({result['holdings_count']}):",
    ])

    for h in result["holdings"]:
        ticker = h.get("ticker", "N/A")
        shares = h.get("shares", 0)
        price = h.get("current_price", 0)
        market_value = h.get("market_value", 0)
        gain_loss = h.get("gain_loss", 0)
        pct = h.get("gain_loss_pct", 0)
        pct_port = h.get("pct_portfolio", 0)

        output.append(f"\n  {ticker}:")
        output.append(f"    Shares: {shares}")
        output.append(f"    Price: ${price:.2f}")
        output.append(f"    Market Value: {format_currency(market_value)}")
        output.append(f"    P&L: {format_currency(gain_loss)} ({format_percent(pct)})")
        output.append(f"    Portfolio: {pct_port:.2f}%")

    summary = result["summary"]
    output.append("\nPortfolio Summary:")
    holdings_value = summary.get('holdings_value', 0)
    cash_amount = shared_cash.get('amount', 0)
    total_value = holdings_value + cash_amount
    output.append(f"  Holdings Value: {format_currency(holdings_value)}")
    output.append(f"  Shared Cash: {format_currency(cash_amount)}")
    output.append(f"  Total Value: {format_currency(total_value)}")
    output.append(f"  Total P&L: {format_currency(summary.get('total_gain_loss', 0))} ({format_percent(summary.get('total_gain_loss_pct', 0))})")

    return "\n".join(output)


def list_all_portfolios() -> dict:
    """List all available portfolios."""
    try:
        root = get_project_root()
        result = list_portfolios(root / "portfolios.json")

        # Get default portfolio name
        try:
            with open(root / "portfolios.json") as f:
                portfolios = json.load(f)
                default = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
        except:
            default = "CORE"

        result["default_portfolio"] = default
        return result
    except FileNotFoundError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Get portfolio status (v3.0 Minimal)")
    parser.add_argument("--portfolio", help="Portfolio name (e.g., CORE, AI_PICKS). Default: metadata.default_portfolio")
    parser.add_argument("--list", action="store_true", help="List all available portfolios")
    parser.add_argument("--format", choices=["json", "human"], default="json", help="Output format (default: json)")
    parser.add_argument("--verbose", action="store_true", help="Include full holding data (default: concise for LLM)")
    args = parser.parse_args()

    if args.list:
        result = list_all_portfolios()
        if args.format == "human":
            if result.get("status") == "error":
                print(f"Error: {result['error']}")
                sys.exit(1)

            shared_cash = result.get("shared_cash", {})
            default_pf = result.get("default_portfolio", "CORE")
            count = len(result.get("portfolios", []))
            print(f"Available Portfolios ({count}) - Default: {default_pf}")
            print("=" * 60)
            print(f"Shared Cash: {format_currency(shared_cash.get('amount', 0))} (Target Buffer: {shared_cash.get('target_buffer_pct', 15)}%)")
            print()
            for p in result["portfolios"]:
                default_marker = " [DEFAULT]" if p["name"] == default_pf else ""
                print(f"  {p['name']}{default_marker}: {p.get('description', '')}")
                print(f"    Holdings: {format_currency(p['holdings_value'])} | "
                      f"Positions: {p['holdings_count']} | "
                      f"P&L: {format_currency(p.get('total_gain_loss', 0))} ({format_percent(p.get('total_gain_loss_pct', 0))})")
        else:
            print(json.dumps(result, indent=2))

        if result.get("status") == "error":
            sys.exit(1)
        return

    result = get_portfolio_status(portfolio_name=args.portfolio, verbose=args.verbose)

    if args.format == "human":
        # Determine actual portfolio name for display
        display_portfolio = args.portfolio
        if display_portfolio is None:
            try:
                root = get_project_root()
                with open(root / "portfolios.json") as f:
                    portfolios = json.load(f)
                    display_portfolio = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
            except:
                display_portfolio = "UNKNOWN"
        print(format_human_readable(result, portfolio_name=display_portfolio))
    else:
        # Add portfolio name to result
        if result["status"] == "success":
            root = get_project_root()
            try:
                with open(root / "portfolios.json") as f:
                    portfolios = json.load(f)
                    result["portfolio"] = args.portfolio or portfolios.get("metadata", {}).get("default_portfolio", "CORE")
            except:
                pass
        print(json.dumps(result, indent=2))

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
