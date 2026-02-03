#!/usr/bin/env python3
"""
Portfolio & Trade Log Updater for LLM Agents (v3.0 Minimal)

Automatically updates portfolios.json and trade_log.csv when trades occur.
LLM agents should call this script instead of manually editing files.

IMPORTANT (v3.0): portfolios.json only stores MINIMAL data:
  - ticker, shares, avg_cost, current_price, status
  - All analysis data goes in analytics/[TICKER]/ folder

Usage:
    python scripts/update_portfolio_and_log.py \
        --ticker TCOM --action BUY --shares 84 --price 61.09 \
        --reasoning "Antitrust oversold condition"

    python scripts/update_portfolio_and_log.py \
        --ticker TCOM --action BUY --shares 84 --price 61.09 \
        --portfolio CORE \
        --reasoning "Antitrust oversold condition"

    # From Python:
    from scripts.update_portfolio_and_log import execute_trade
    execute_trade(ticker="TCOM", action="BUY", shares=84, price=61.09,
                  portfolio_name="CORE", reasoning="Antitrust oversold")
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List


def execute_trade(
    ticker: str,
    action: str,
    shares: int,
    price: float,
    reasoning: str,
    evidence_files: Optional[List[str]] = None,
    timestamp: Optional[str] = None,
    portfolio_name: Optional[str] = None,
    portfolios_path: Optional[str] = None
) -> dict:
    """
    Execute a trade: updates both portfolios.json and trade_log.csv

    Args:
        ticker: Stock ticker (uppercase)
        action: BUY, SELL, or TRIM
        shares: Number of shares
        price: Execution price per share
        reasoning: Trade rationale
        evidence_files: List of supporting file paths
        timestamp: ISO 8601 timestamp (auto-generated if None)
        portfolio_name: Portfolio name (e.g., "CORE", "AI_PICKS"). Default if None.
        portfolios_path: Path to portfolios.json (default: project root)

    Returns:
        dict with updated portfolio state and trade details

    Raises:
        FileNotFoundError: If portfolios.json doesn't exist
        ValueError: For invalid inputs (ticker, action, shares, price, etc.)

    Note (v3.0): Analysis data should be stored in analytics/[TICKER]/ folder,
                  not in portfolios.json.
    """
    # Import local common module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from common import (
        get_project_root,
        get_portfolio,
        get_shared_cash,
        update_shared_cash,
        update_portfolio,
        recalculate_portfolio_totals,
        load_portfolios,
        save_portfolios,
        log_trade,
        list_portfolios,
    )

    # Validate inputs
    ticker = ticker.upper().strip()

    # Validate ticker format
    if not ticker or not ticker.isalpha() or len(ticker) > 5:
        raise ValueError(f"Invalid ticker format: {ticker}. Must be 1-5 letters.")

    # Validate action
    action = action.upper().strip()
    if action not in ['BUY', 'SELL', 'TRIM']:
        raise ValueError(f"Invalid action: {action}. Must be BUY, SELL, or TRIM")

    # Validate shares
    if shares <= 0:
        raise ValueError(f"Shares must be positive, got: {shares}")

    if not isinstance(shares, int):
        raise ValueError(f"Shares must be an integer, got: {type(shares)}")

    # Validate price
    if price < 0:
        raise ValueError(f"Price cannot be negative, got: {price}")

    if price > 100000:
        raise ValueError(f"Price seems unreasonably high: ${price:.2f}")

    if price == 0:
        raise ValueError(f"Price cannot be zero")

    # Note (v3.0): thesis_status removed - use analytics/[TICKER]/_investment_thesis.md instead

    # Validate reasoning
    if not reasoning or not reasoning.strip():
        raise ValueError("Reasoning cannot be empty")

    # Determine path to portfolios.json
    if portfolios_path is None:
        root = get_project_root()
        portfolios_path = root / 'portfolios.json'
    else:
        portfolios_path = Path(portfolios_path)

    # Check if portfolios.json exists
    if not portfolios_path.exists():
        raise FileNotFoundError(f"Portfolios file not found: {portfolios_path}")

    # Load portfolio and shared cash
    portfolio = get_portfolio(portfolio_name, portfolios_path, include_cash=True)
    shared_cash_data = get_shared_cash(portfolios_path)
    shared_cash_amount = shared_cash_data.get('amount', 0)

    # Get actual portfolio name (in case None was passed)
    if portfolio_name is None:
        all_portfolios = load_portfolios(portfolios_path)
        actual_portfolio_name = all_portfolios.get("metadata", {}).get("default_portfolio", "CORE")
    else:
        actual_portfolio_name = portfolio_name

    # Find or create holding
    holding = None
    for h in portfolio['holdings']:
        if h['ticker'] == ticker:
            holding = h
            break

    # Determine which summary key to use
    summary_key = "summary" if "summary" in portfolio else "portfolio_summary"

    if action == 'BUY':
        if holding is None:
            # Create new holding (v3.0 minimal schema only)
            holding = {
                'ticker': ticker,
                'shares': shares,
                'avg_cost': round(price, 2),
                'current_price': round(price, 2),
                'status': 'active'
            }
            portfolio['holdings'].append(holding)
        else:
            # Add to existing position
            old_shares = holding['shares']
            old_cost = holding['avg_cost']
            total_cost = (old_shares * old_cost) + (shares * price)
            total_shares = old_shares + shares

            holding['shares'] = total_shares
            holding['avg_cost'] = round(total_cost / total_shares, 2)
            holding['current_price'] = price
            holding['market_value'] = round(total_shares * price, 2)
            holding['gain_loss'] = round(holding['market_value'] - (total_shares * holding['avg_cost']), 2)
            holding['gain_loss_pct'] = round((holding['gain_loss'] / (total_shares * holding['avg_cost'])) * 100, 2)

        # Update shared cash
        cost = shares * price
        shared_cash_amount = round(shared_cash_amount - cost, 2)

    elif action in ['SELL', 'TRIM']:
        if holding is None:
            # Show available portfolios to help user
            available = list_portfolios(portfolios_path)
            port_list = [p['name'] for p in available.get('portfolios', [])]
            raise ValueError(
                f"Cannot sell {ticker}: position not found in portfolio '{actual_portfolio_name}'. "
                f"Available portfolios: {port_list}"
            )

        if shares > holding['shares']:
            raise ValueError(f"Cannot sell {shares} shares of {ticker}: only {holding['shares']} available")

        cost_basis = holding['avg_cost']
        realized_pl = shares * (price - cost_basis)
        pl_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0.0

        # Calculate portfolio % before selling
        holdings_value = sum(h['market_value'] for h in portfolio['holdings'])
        total_value = holdings_value + shared_cash_amount
        portfolio_pct = (holding['market_value'] / total_value) * 100 if total_value > 0 else 0

        # Log to trade_log FIRST (before modifying holding)
        trade = log_trade(
            ticker=ticker,
            action=action,
            shares=shares,
            price=price,
            cost_basis=cost_basis,
            portfolio_pct=round(portfolio_pct, 2),
            thesis_status="",  # v3.0: removed - use analytics/ folder
            reasoning=reasoning,
            evidence_files=evidence_files or [],
            timestamp=timestamp,
            portfolio_name=actual_portfolio_name
        )

        # Update holding
        holding['shares'] -= shares
        holding['market_value'] = round(holding['shares'] * price, 2)

        if holding['shares'] == 0:
            # Remove empty position
            portfolio['holdings'].remove(holding)
        else:
            holding['gain_loss'] = round(holding['market_value'] - (holding['shares'] * holding['avg_cost']), 2)
            holding['gain_loss_pct'] = round((holding['gain_loss'] / (holding['shares'] * holding['avg_cost'])) * 100, 2)

        # Update shared cash
        proceeds = shares * price
        shared_cash_amount = round(shared_cash_amount + proceeds, 2)

    # Recalculate portfolio totals with shared cash
    portfolio = recalculate_portfolio_totals(portfolio, shared_cash_amount)

    # Get calculated values for output
    total_holdings_value = portfolio[summary_key].get('holdings_value', sum(h['market_value'] for h in portfolio['holdings']))
    total_value = total_holdings_value + shared_cash_amount
    cash_amount = shared_cash_amount

    # Update metadata
    if 'metadata' not in portfolio:
        portfolio['metadata'] = {}
    portfolio['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    # Save portfolio and shared cash
    update_shared_cash(shared_cash_amount, portfolios_path)
    update_portfolio(actual_portfolio_name, portfolio, portfolios_path, shared_cash_amount)

    # Log BUY trades to trade_log (SELL/TRIM already logged above)
    if action == 'BUY':
        # Find the holding to get its portfolio %
        holding = next((h for h in portfolio['holdings'] if h['ticker'] == ticker), None)
        if holding:
            portfolio_pct = holding['pct_portfolio']
        else:
            portfolio_pct = 0.0

        trade = log_trade(
            ticker=ticker,
            action=action,
            shares=shares,
            price=price,
            cost_basis=0.0,  # New position
            portfolio_pct=portfolio_pct,
            thesis_status="",  # v3.0: removed - use analytics/ folder
            reasoning=reasoning,
            evidence_files=evidence_files or [],
            timestamp=timestamp,
            portfolio_name=actual_portfolio_name
        )

    cash_pct = round((cash_amount / total_value) * 100, 2) if total_value > 0 else 0
    print(f"✓ Trade executed: {action} {shares} {ticker} @ ${price:.2f}")
    print(f"  Portfolio: {actual_portfolio_name}")
    print(f"  Shared Cash: ${cash_amount:,.2f} ({cash_pct:.2f}%)")
    print(f"  Total Value: ${total_value:,.2f}")

    return {
        'trade': trade,
        'portfolio': portfolio,
        'holding': holding,
        'cash': cash_amount,
        'total_value': total_value,
        'portfolio_name': actual_portfolio_name
    }


def main():
    """CLI interface for trade execution"""
    parser = argparse.ArgumentParser(
        description='Execute trade and update portfolios.json + trade_log.csv (v3.0 Minimal)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy shares (uses default portfolio)
  python scripts/update_portfolio_and_log.py --ticker TCOM --action BUY --shares 84 --price 61.09 --reasoning "Antitrust oversold"

  # Buy shares in specific portfolio
  python scripts/update_portfolio_and_log.py --ticker TCOM --action BUY --shares 84 --price 61.09 --portfolio CORE --reasoning "Antitrust oversold"

  # Sell shares
  python scripts/update_portfolio_and_log.py --ticker LAES --action SELL --shares 5000 --price 4.50 --portfolio CORE --reasoning "Trimming position"

  # Trim position
  python scripts/update_portfolio_and_log.py --ticker PONY --action TRIM --shares 92 --price 16.56 --portfolio CORE --reasoning "Reduce concentration"

Note (v3.0): Analysis data should be stored in analytics/[TICKER]/ folder,
              not in portfolios.json. Use analytics_generator skill to create analysis files.
        """
    )

    parser.add_argument('--ticker', required=True, help='Stock ticker (e.g., TCOM)')
    parser.add_argument('--action', required=True, choices=['BUY', 'SELL', 'TRIM'], help='Trade action')
    parser.add_argument('--shares', required=True, type=int, help='Number of shares')
    parser.add_argument('--price', required=True, type=float, help='Execution price per share')
    parser.add_argument('--reasoning', required=True, help='Trade rationale')
    parser.add_argument('--evidence', nargs='*', default=[], help='Evidence file paths')
    parser.add_argument('--timestamp', help='ISO 8601 timestamp (default: now)')
    parser.add_argument('--portfolio', help='Portfolio name (e.g., CORE, AI_PICKS). Default: metadata.default_portfolio')

    args = parser.parse_args()

    try:
        result = execute_trade(
            ticker=args.ticker,
            action=args.action,
            shares=args.shares,
            price=args.price,
            reasoning=args.reasoning,
            evidence_files=args.evidence,
            timestamp=args.timestamp,
            portfolio_name=args.portfolio
        )
        print(json.dumps({
            'status': 'success',
            'trade': {
                'ticker': result['trade']['ticker'],
                'action': result['trade']['action'],
                'shares': result['trade']['shares'],
                'price': result['trade']['price'],
                'portfolio_pct': result['trade']['portfolio_pct']
            },
            'portfolio': {
                'name': result.get('portfolio_name', 'UNKNOWN'),
                'total_value': result['total_value'],
                'cash': result['cash']
            }
        }, indent=2))

    except Exception as e:
        print(json.dumps({'status': 'error', 'message': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
