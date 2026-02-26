#!/usr/bin/env python3
"""
Get holdings summary from portfolio with P/L calculations.

This script extracts holdings from the specified portfolio and calculates
market value, gain/loss, and gain/loss percentage for each position.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude"))

from shared.data_access import DataAccess


def get_holdings_with_pnl(portfolio_name: Optional[str] = None) -> Dict:
    """
    Get holdings with P/L calculations from portfolio.

    Args:
        portfolio_name: Portfolio name (e.g., "CORE", "AI_PICKS").
                       If None, uses default portfolio from metadata.

    Returns:
        Dict with portfolio summary including:
        - portfolio_name: str
        - description: str
        - cash: float (shared cash pool)
        - holdings: List[Dict] with ticker, shares, avg_cost, current_price,
                     market_value, gain_loss, gain_loss_pct, status
        - summary: Dict with totals

    Raises:
        ValueError: If portfolio not found
    """
    da = DataAccess()

    # Load portfolio
    try:
        portfolio = da.get_portfolio(portfolio_name)
    except ValueError as e:
        raise ValueError(f"Portfolio '{portfolio_name}' not found. Available: {list(da.load_portfolios().get('portfolios', {}).keys())}")

    # Get shared cash
    cash_data = da.get_shared_cash()
    cash_amount = cash_data.get("amount", 0.0)

    # Extract holdings with P/L calculations
    holdings_list = []
    for holding in portfolio.get("holdings", []):
        ticker = holding.get("ticker", "").upper()
        shares = holding.get("shares", 0)
        avg_cost = holding.get("avg_cost", 0.0)
        current_price = holding.get("current_price", 0.0)
        status = holding.get("status", "active")

        # Calculate market value
        market_value = shares * current_price

        # Calculate cost basis
        cost_basis = shares * avg_cost

        # Calculate gain/loss
        gain_loss = market_value - cost_basis

        # Calculate gain/loss percentage
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0.0

        holdings_list.append({
            "ticker": ticker,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_price": current_price,
            "market_value": market_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "status": status
        })

    # Get portfolio summary
    summary = portfolio.get("summary", {})

    return {
        "portfolio_name": portfolio_name or list(da.load_portfolios().get("metadata", {}).get("default_portfolio", "CORE")),
        "description": portfolio.get("description", ""),
        "cash": cash_amount,
        "holdings": holdings_list,
        "summary": {
            "holdings_value": summary.get("holdings_value", sum(h["market_value"] for h in holdings_list)),
            "total_cost_basis": summary.get("total_cost_basis", sum(h["shares"] * h["avg_cost"] for h in holdings_list)),
            "total_gain_loss": summary.get("total_gain_loss", sum(h["gain_loss"] for h in holdings_list)),
            "total_gain_loss_pct": summary.get("total_gain_loss_pct", 0.0),
            "holdings_count": len(holdings_list)
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Get holdings summary with P/L calculations")
    parser.add_argument("--portfolio", type=str, help="Portfolio name (e.g., CORE, LLM_HELP)")
    parser.add_argument("--format", type=str, default="json", choices=["json", "table"], help="Output format")
    args = parser.parse_args()

    try:
        result = get_holdings_with_pnl(args.portfolio)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        elif args.format == "table":
            print(f"\n=== {result['portfolio_name']} Portfolio ===")
            print(f"Cash: ${result['cash']:.2f}\n")
            print(f"{'Ticker':<8} {'Shares':>8} {'Avg Cost':>10} {'Price':>10} {'Value':>12} {'P/L':>12} {'P/L %':>8}")
            print("-" * 80)
            for h in result["holdings"]:
                pl_pct_str = f"{h['gain_loss_pct']:+.1f}%"
                print(f"{h['ticker']:<8} {h['shares']:>8} ${h['avg_cost']:>8.2f} ${h['current_price']:>8.2f} ${h['market_value']:>10.2f} ${h['gain_loss']:>10.2f} {pl_pct_str:>8}")
            print("-" * 80)
            summary = result["summary"]
            total_pl_pct_str = f"{summary['total_gain_loss_pct']:+.1f}%"
            print(f"{'TOTAL':<8} {summary['holdings_count']:>8} positions: ${summary['holdings_value']:>10.2f} ${summary['total_gain_loss']:>10.2f} {total_pl_pct_str:>8}")
            print()

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
