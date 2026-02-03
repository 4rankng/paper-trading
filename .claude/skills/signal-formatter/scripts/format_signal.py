#!/usr/bin/env python3
"""
Format a trading signal based on the standard template.
"""
import argparse
import sys

TEMPLATE = """## {ticker} Signal

**Action:** {action}
**Driver Class:** {driver_class}
**Confidence:** {confidence}

### Levels
- **Entry:** {entry}
- **Exit:** {exit_target}
- **Stop:** {stop_loss}

### Position Sizing
- **Size:** {size}
- **Timeframe:** {timeframe}

### Top 3 Risks
1. {risk1}
2. {risk2}
3. {risk3}

### Opportunity Cost
Not buying: {opportunity_cost}
Expected alpha: {alpha}

### Machine Logic
{machine_logic}

### Benchmark Comparison
(Paste from benchmark-template.md)
"""

def main():
    parser = argparse.ArgumentParser(description='Format a trading signal.')
    parser.add_argument('--ticker', required=True, help='Stock ticker')
    parser.add_argument('--action', required=True, choices=['BUY', 'SELL', 'HOLD', 'TRIM'], help='Action')
    parser.add_argument('--driver', required=True, choices=['HYPE_MACHINE', 'EARNINGS_MACHINE', 'MEAN_REVERSION_MACHINE', 'SECULAR_GROWTH'], help='Driver Class')
    parser.add_argument('--confidence', required=True, choices=['HIGH', 'MEDIUM', 'LOW'], help='Confidence level')
    parser.add_argument('--entry', required=True, help='Entry price/condition')
    parser.add_argument('--exit', required=True, help='Exit target')
    parser.add_argument('--stop', required=True, help='Stop loss')
    parser.add_argument('--size', required=True, help='Position size (e.g., "$1,000" or "5%")')
    parser.add_argument('--timeframe', required=True, help='Timeframe (e.g., "3 months")')
    parser.add_argument('--risk1', required=True, help='Risk 1')
    parser.add_argument('--risk2', required=True, help='Risk 2')
    parser.add_argument('--risk3', required=True, help='Risk 3')
    parser.add_argument('--opp-cost', required=True, help='Opportunity cost (ticker)')
    parser.add_argument('--alpha', required=True, help='Expected alpha')
    parser.add_argument('--logic', required=True, help='Machine logic explanation')

    args = parser.parse_args()

    signal = TEMPLATE.format(
        ticker=args.ticker.upper(),
        action=args.action.upper(),
        driver_class=args.driver.upper(),
        confidence=args.confidence.upper(),
        entry=args.entry,
        exit_target=args.exit,
        stop_loss=args.stop,
        size=args.size,
        timeframe=args.timeframe,
        risk1=args.risk1,
        risk2=args.risk2,
        risk3=args.risk3,
        opportunity_cost=args.opp_cost,
        alpha=args.alpha,
        machine_logic=args.logic
    )

    print(signal)

if __name__ == '__main__':
    main()
