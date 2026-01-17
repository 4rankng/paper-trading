#!/usr/bin/env python3
"""
Add a new stock holding to the portfolio.

Usage:
    python add_holding.py --ticker NVDA --shares 100 --price 150.25 --thesis-status PENDING
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


def add_holding(ticker: str, shares: int, price: float, thesis_status: str = 'PENDING', thesis: str = '') -> dict:
    """
    Add a new holding to the portfolio.

    Args:
        ticker: Stock ticker
        shares: Number of shares
        price: Purchase price per share
        thesis_status: Thesis validation status
        thesis: Investment thesis

    Returns:
        Result dictionary
    """
    project_root = get_project_root()
    portfolio_path = project_root / 'portfolio.json'

    if not portfolio_path.exists():
        return {
            'status': 'error',
            'error': 'Portfolio file not found'
        }

    try:
        with open(portfolio_path, 'r') as f:
            portfolio = json.load(f)

        ticker = ticker.upper()

        # Check if holding already exists
        for h in portfolio['holdings']:
            if h['ticker'] == ticker:
                return {
                    'status': 'error',
                    'error': f'Holding already exists for {ticker}. Use update_portfolio_and_log.py instead.'
                }

        # Calculate market value
        market_value = shares * price

        # Create new holding
        new_holding = {
            'ticker': ticker,
            'shares': shares,
            'avg_cost': price,
            'current_price': price,
            'market_value': round(market_value, 2),
            'gain_loss': 0.0,
            'gain_loss_pct': 0.0,
            'pct_portfolio': 0.0,  # Will recalculate
            'status': 'active',
            'thesis_status': thesis_status,
            'thesis_validation_confidence': 'MEDIUM',
            'time_horizon': 'swing',
            'contracts_validated': False,
            'sell_signal_triggered': False,
            'name': ticker,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'invalidation_level': 'TBD',
            'technical_alignment': 'TBD',
            'thesis': thesis or f'{ticker} investment position',
            'major_partnerships': [],
            'last_news_update': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        portfolio['holdings'].append(new_holding)

        # Update cash
        cost = shares * price
        portfolio['cash']['amount'] = round(portfolio['cash']['amount'] - cost, 2)

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
            'ticker': ticker,
            'shares': shares,
            'price': price,
            'market_value': round(market_value, 2),
            'total_value': round(total_value, 2)
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Add holding to portfolio')
    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker')
    parser.add_argument('--shares', required=True, type=int, help='Number of shares')
    parser.add_argument('--price', required=True, type=float, help='Purchase price')
    parser.add_argument('--thesis-status', default='PENDING',
                       choices=['PENDING', 'VALIDATING', 'VALIDATED', 'FAILED', 'TRANSFORMING', 'INVALIDATED'],
                       help='Thesis status')
    parser.add_argument('--thesis', type=str, help='Investment thesis')

    args = parser.parse_args()

    result = add_holding(args.ticker, args.shares, args.price, args.thesis_status, args.thesis)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
