#!/usr/bin/env python3
"""
Remove a stock holding from the portfolio (SELL or TRIM).

Usage:
    python remove_holding.py --ticker LAES --shares 5000 --action SELL
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def remove_holding(ticker: str, shares: int, action: str = 'SELL') -> dict:
    """
    Remove a holding from the portfolio.

    Args:
        ticker: Stock ticker
        shares: Number of shares to sell
        action: SELL (exit position) or TRIM (reduce position)

    Returns:
        Result dictionary
    """
    project_root = get_project_root()
    portfolio_path = project_root / 'portfolio.json'
    trade_log_path = project_root / 'trade_log.csv'

    if not portfolio_path.exists():
        return {
            'status': 'error',
            'error': 'Portfolio file not found'
        }

    action = action.upper()
    if action not in ['SELL', 'TRIM']:
        return {
            'status': 'error',
            'error': f'Invalid action: {action}. Must be SELL or TRIM'
        }

    try:
        with open(portfolio_path, 'r') as f:
            portfolio = json.load(f)

        ticker = ticker.upper()
        holding = None
        for h in portfolio['holdings']:
            if h['ticker'] == ticker:
                holding = h
                break

        if not holding:
            return {
                'status': 'error',
                'error': f'Holding not found: {ticker}'
            }

        if shares > holding['shares']:
            return {
                'status': 'error',
                'error': f'Cannot sell {shares} shares of {ticker}: only {holding["shares"]} available'
            }

        # Calculate P&L
        cost_basis = holding['avg_cost']
        price = holding['current_price']
        realized_pl = shares * (price - cost_basis)
        pl_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0.0

        # Calculate portfolio % before selling
        total_value = portfolio['portfolio_summary']['total_value']
        portfolio_pct = (holding['market_value'] / total_value) * 100

        # Log to trade_log
        trade_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'ticker': ticker,
            'action': action,
            'shares': shares,
            'price': price,
            'cost_basis': cost_basis,
            'portfolio_pct': round(portfolio_pct, 2),
            'thesis_status': holding.get('thesis_status', 'PENDING'),
            'reasoning': f'{action} position'
        }

        # Append to trade_log.csv
        import csv
        file_exists = trade_log_path.exists()
        with open(trade_log_path, 'a', newline='') as f:
            fieldnames = ['timestamp', 'ticker', 'action', 'shares', 'price', 'cost_basis', 'portfolio_pct', 'thesis_status', 'reasoning']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(trade_entry)

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
        portfolio['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Save portfolio
        with open(portfolio_path, 'w') as f:
            json.dump(portfolio, f, indent=2)

        return {
            'status': 'success',
            'action': action,
            'ticker': ticker,
            'shares': shares,
            'price': price,
            'proceeds': round(proceeds, 2),
            'realized_pl': round(realized_pl, 2),
            'realized_pl_pct': round(pl_pct, 2),
            'total_value': round(total_value, 2)
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Remove holding from portfolio')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker')
    parser.add_argument('--shares', required=True, type=int, help='Number of shares')
    parser.add_argument('--action', default='SELL', choices=['SELL', 'TRIM'],
                       help='Action: SELL (exit) or TRIM (reduce)')

    args = parser.parse_args()

    result = remove_holding(args.ticker, args.shares, args.action)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
