#!/usr/bin/env python3
"""
Get current portfolio status and holdings.

Usage:
    python get_portfolio.py
    python get_portfolio.py --format human
"""
import argparse
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def get_portfolio_status() -> dict:
    """
    Get current portfolio status.

    Returns:
        Dictionary with portfolio state
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

        return {
            'status': 'success',
            'timestamp': portfolio.get('metadata', {}).get('last_updated'),
            'cash': portfolio.get('cash', {}),
            'holdings_count': len(portfolio.get('holdings', [])),
            'holdings': portfolio.get('holdings', []),
            'summary': portfolio.get('portfolio_summary', {})
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def format_human_readable(result: dict) -> str:
    """Format portfolio status as human-readable text."""
    if result['status'] == 'error':
        return f"Error: {result['error']}"

    output = ["Portfolio Status", "=" * 60]
    output.append(f"Cash: ${result['cash']['amount']:,.2f}")
    output.append(f"\nHoldings ({result['holdings_count']}):")

    for h in result['holdings']:
        ticker = h.get('ticker', 'N/A')
        shares = h.get('shares', 0)
        price = h.get('current_price', 0)
        market_value = h.get('market_value', 0)
        gain_loss = h.get('gain_loss', 0)
        pct = h.get('gain_loss_pct', 0)
        pct_port = h.get('pct_portfolio', 0)

        output.append(f"\n  {ticker}:")
        output.append(f"    Shares: {shares}")
        output.append(f"    Price: ${price:.2f}")
        output.append(f"    Market Value: ${market_value:,.2f}")
        output.append(f"    P&L: ${gain_loss:+,.2f} ({pct:+.2f}%)")
        output.append(f"    Portfolio: {pct_port:.2f}%")

    summary = result['summary']
    output.append(f"\nPortfolio Summary:")
    output.append(f"  Total Value: ${summary.get('total_value', 0):,.2f}")
    output.append(f"  Cash: ${summary.get('cash_amount', 0):,.2f} ({summary.get('cash_pct', 0):.2f}%)")
    output.append(f"  Total P&L: ${summary.get('total_gain_loss', 0):+,.2f} ({summary.get('total_gain_loss_pct', 0):.2f}%)")

    return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Get portfolio status')
    parser.add_argument('--format', choices=['json', 'human'], default='json',
                       help='Output format (default: json)')

    args = parser.parse_args()

    result = get_portfolio_status()

    if args.format == 'human':
        print(format_human_readable(result))
    else:
        print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
