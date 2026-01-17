#!/usr/bin/env python3
"""
Portfolio & Trade Log Updater for LLM Agents

Automatically updates portfolio.json and trade_log.csv when trades occur.
LLM agents should call this script instead of manually editing files.

Usage:
    python scripts/update_portfolio_and_log.py \
        --ticker TCOM --action BUY --shares 84 --price 61.09 \
        --thesis-status PENDING \
        --reasoning "Antitrust oversold condition"

    # From Python:
    from scripts.update_portfolio_and_log import execute_trade
    execute_trade(ticker="TCOM", action="BUY", shares=84, price=61.09,
                  thesis_status="PENDING", reasoning="Antitrust oversold")
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Platform-specific file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    # Windows doesn't have fcntl
    HAS_FCNTL = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


def lock_file(file_handle):
    """
    Lock a file handle for exclusive access (cross-platform).

    Args:
        file_handle: Open file handle to lock
    """
    if HAS_FCNTL:
        # Unix/Linux/macOS
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX)
    elif HAS_MSVCRT:
        # Windows
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)


def unlock_file(file_handle):
    """
    Unlock a file handle (cross-platform).

    Args:
        file_handle: Open file handle to unlock
    """
    if HAS_FCNTL:
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    elif HAS_MSVCRT:
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLOCK, 1)


def execute_trade(
    ticker: str,
    action: str,
    shares: int,
    price: float,
    thesis_status: str,
    reasoning: str,
    evidence_files: Optional[List[str]] = None,
    timestamp: Optional[str] = None,
    portfolio_path: Optional[str] = None
) -> dict:
    """
    Execute a trade: updates both portfolio.json and trade_log.csv

    Args:
        ticker: Stock ticker (uppercase)
        action: BUY, SELL, or TRIM
        shares: Number of shares
        price: Execution price per share
        thesis_status: PENDING, VALIDATING, VALIDATED, FAILED
        reasoning: Trade rationale
        evidence_files: List of supporting file paths
        timestamp: ISO 8601 timestamp (auto-generated if None)
        portfolio_path: Path to portfolio.json (default: project root)

    Returns:
        dict with updated portfolio state and trade details
    """
    # Import shared agent_helpers from data-fetching skill
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'skills' / 'data-fetching' / 'scripts'))
    from agent_helpers.trade_log_manager import TradeLogManager
    from agent_helpers.common import get_project_root

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

    # Validate thesis_status
    valid_statuses = ['PENDING', 'VALIDATING', 'VALIDATED', 'FAILED', 'TRANSFORMING', 'INVALIDATED']
    thesis_status = thesis_status.upper().strip()
    if thesis_status not in valid_statuses:
        raise ValueError(f"Invalid thesis_status: {thesis_status}. Must be one of: {', '.join(valid_statuses)}")

    # Validate reasoning
    if not reasoning or not reasoning.strip():
        raise ValueError("Reasoning cannot be empty")

    # Load portfolio with file locking
    if portfolio_path is None:
        portfolio_path = get_project_root() / 'portfolio.json'
    else:
        portfolio_path = Path(portfolio_path)

    # Open file with exclusive lock for reading
    file_handle = open(portfolio_path, 'r')
    try:
        lock_file(file_handle)
        portfolio = json.load(file_handle)
    finally:
        unlock_file(file_handle)
        file_handle.close()

    # Find or create holding
    holding = None
    for h in portfolio['holdings']:
        if h['ticker'] == ticker:
            holding = h
            break

    if action == 'BUY':
        if holding is None:
            # Create new holding
            holding = {
                'ticker': ticker,
                'shares': shares,
                'avg_cost': price,
                'current_price': price,
                'market_value': shares * price,
                'gain_loss': 0.0,
                'gain_loss_pct': 0.0,
                'pct_portfolio': 0.0,  # Will recalculate
                'status': 'active',
                'thesis_status': thesis_status,
                'thesis_validation_confidence': 'MEDIUM',
                'time_horizon': 'swing',
                'contracts_validated': False,
                'sell_signal_triggered': False,
                'name': ticker,  # Placeholder
                'sector': 'Unknown',
                'industry': 'Unknown',
                'invalidation_level': 'TBD',
                'technical_alignment': 'TBD',
                'thesis': reasoning,
                'major_partnerships': [],
                'last_news_update': datetime.utcnow().isoformat() + 'Z'
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

        # Update cash
        cost = shares * price
        portfolio['cash']['amount'] = round(portfolio['cash']['amount'] - cost, 2)

    elif action in ['SELL', 'TRIM']:
        if holding is None:
            raise ValueError(f"Cannot sell {ticker}: position not found in portfolio")

        if shares > holding['shares']:
            raise ValueError(f"Cannot sell {shares} shares of {ticker}: only {holding['shares']} available")

        cost_basis = holding['avg_cost']
        realized_pl = shares * (price - cost_basis)
        pl_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0.0

        # Calculate portfolio % before selling
        total_value = portfolio['portfolio_summary']['total_value']
        portfolio_pct = (holding['market_value'] / total_value) * 100

        # Log to trade_log FIRST (before modifying holding)
        tlm = TradeLogManager()
        trade = tlm.log_trade(
            ticker=ticker,
            action=action,
            shares=shares,
            price=price,
            cost_basis=cost_basis,
            portfolio_pct=round(portfolio_pct, 2),
            thesis_status=thesis_status,
            reasoning=reasoning,
            evidence_files=evidence_files or [],
            timestamp=timestamp
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

        # Update cash
        proceeds = shares * price
        portfolio['cash']['amount'] = round(portfolio['cash']['amount'] + proceeds, 2)

    # Recalculate portfolio totals
    total_holdings_value = sum(h['market_value'] for h in portfolio['holdings'])
    total_value = total_holdings_value + portfolio['cash']['amount']
    total_cost = sum(h['shares'] * h['avg_cost'] for h in portfolio['holdings'])
    total_gl = sum(h['gain_loss'] for h in portfolio['holdings'])

    portfolio['portfolio_summary']['total_value'] = round(total_value, 2)
    portfolio['portfolio_summary']['cash_amount'] = portfolio['cash']['amount']
    portfolio['portfolio_summary']['cash_pct'] = round((portfolio['cash']['amount'] / total_value) * 100, 2)
    portfolio['portfolio_summary']['total_cost_basis'] = round(total_cost, 2)
    portfolio['portfolio_summary']['total_gain_loss'] = round(total_gl, 2)
    portfolio['portfolio_summary']['total_gain_loss_pct'] = round((total_gl / total_cost) * 100, 2) if total_cost > 0 else 0

    # Update position percentages
    for h in portfolio['holdings']:
        h['pct_portfolio'] = round((h['market_value'] / total_value) * 100, 2)

    # Update metadata
    portfolio['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    # Save portfolio with file locking
    file_handle = open(portfolio_path, 'w')
    try:
        lock_file(file_handle)
        json.dump(portfolio, file_handle, indent=2)
        file_handle.flush()  # Ensure data is written before unlocking
    finally:
        unlock_file(file_handle)
        file_handle.close()

    # Log BUY trades to trade_log (SELL/TRIM already logged above)
    if action == 'BUY':
        tlm = TradeLogManager()
        total_value = portfolio['portfolio_summary']['total_value']
        # Find the holding to get its portfolio %
        holding = next(h for h in portfolio['holdings'] if h['ticker'] == ticker)
        portfolio_pct = holding['pct_portfolio']

        trade = tlm.log_trade(
            ticker=ticker,
            action=action,
            shares=shares,
            price=price,
            cost_basis=0.0,  # New position
            portfolio_pct=portfolio_pct,
            thesis_status=thesis_status,
            reasoning=reasoning,
            evidence_files=evidence_files or [],
            timestamp=timestamp
        )

    print(f"✓ Trade executed: {action} {shares} {ticker} @ ${price:.2f}")
    print(f"  Portfolio updated: ${total_value:,.2f}")
    print(f"  Cash: ${portfolio['cash']['amount']:,.2f} ({portfolio['portfolio_summary']['cash_pct']:.2f}%)")

    return {
        'trade': trade,
        'portfolio': portfolio,
        'holding': holding,
        'cash': portfolio['cash']['amount'],
        'total_value': total_value
    }


def main():
    """CLI interface for trade execution"""
    parser = argparse.ArgumentParser(
        description='Execute trade and update portfolio.json + trade_log.csv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy shares
  python scripts/update_portfolio_and_log.py --ticker TCOM --action BUY --shares 84 --price 61.09 --thesis-status PENDING --reasoning "Antitrust oversold"

  # Sell shares
  python scripts/update_portfolio_and_log.py --ticker LAES --action SELL --shares 5000 --price 4.50 --thesis-status VALIDATING --reasoning "Trimming position"

  # Trim position
  python scripts/update_portfolio_and_log.py --ticker PONY --action TRIM --shares 92 --price 16.56 --thesis-status VALIDATING --reasoning "Reduce concentration"
        """
    )

    parser.add_argument('--ticker', required=True, help='Stock ticker (e.g., TCOM)')
    parser.add_argument('--action', required=True, choices=['BUY', 'SELL', 'TRIM'], help='Trade action')
    parser.add_argument('--shares', required=True, type=int, help='Number of shares')
    parser.add_argument('--price', required=True, type=float, help='Execution price per share')
    parser.add_argument('--thesis-status', required=True, choices=['PENDING', 'VALIDATING', 'VALIDATED', 'FAILED', 'TRANSFORMING', 'INVALIDATED'], help='Thesis status')
    parser.add_argument('--reasoning', required=True, help='Trade rationale')
    parser.add_argument('--evidence', nargs='*', default=[], help='Evidence file paths')
    parser.add_argument('--timestamp', help='ISO 8601 timestamp (default: now)')
    parser.add_argument('--portfolio', help='Path to portfolio.json (default: project root)')

    args = parser.parse_args()

    try:
        result = execute_trade(
            ticker=args.ticker,
            action=args.action,
            shares=args.shares,
            price=args.price,
            thesis_status=args.thesis_status,
            reasoning=args.reasoning,
            evidence_files=args.evidence,
            timestamp=args.timestamp,
            portfolio_path=args.portfolio
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
                'total_value': result['total_value'],
                'cash': result['cash']
            }
        }, indent=2))

    except Exception as e:
        print(json.dumps({'status': 'error', 'message': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
