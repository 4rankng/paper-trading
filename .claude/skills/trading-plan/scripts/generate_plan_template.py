#!/usr/bin/env python3
"""
Generate a trading plan template file.
"""
import argparse
import os
from datetime import datetime
from pathlib import Path

TEMPLATE = """# {ticker} Trading Plan ({timeframe})

**Current Price:** $XX.XX
**Recommendation:** BUY/AVOID
**Machine:** {machine_type}
**Approach:** {approach}
**Confidence:** HIGH/MEDIUM/LOW
**R:R:** X:1

## Signal

**Entry:** $XX.XX
**Target:** $XX.XX (+X%)
**Stop:** $XX.XX (-X%)

**Position Size:** {position_size}

## Rationale

[2-3 sentences max, tailored to timeframe]
- Incorporate top bull/bear points from debate
- Reflect consensus strength from vote tally
- Calibrate confidence level based on analyst conviction

## Machine Logic

**Why {machine_type} for {timeframe}:**
- [1 sentence]
- [1 sentence]

**Not other machines:**
- [1 sentence each]

## Catalysts

{catalysts}

## Risk

**Top 3 Risks:**
1. [Risk from debate bear case] - [Mitigation from debate]
2. [Risk from debate bear case] - [Mitigation from debate]
3. [Risk from debate bear case] - [Mitigation from debate]

## Exit Triggers

- [Trigger]
- [Trigger]
- [Trigger]

**Generated:** {date}
**Next Review:** {review_date}
"""

def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    # Go up until we find .claude or reach root
    for parent in [current] + list(current.parents):
        if (parent / ".claude").exists():
             return parent
    return Path.cwd() # Fallback

def main():
    parser = argparse.ArgumentParser(description='Generate trading plan template.')
    parser.add_argument('--ticker', required=True, help='Stock ticker')
    parser.add_argument('--timeframe', required=True, choices=['1d', '3d', '1w', '1m', '3m', '6m', '1y'], help='Timeframe')
    parser.add_argument('--capital', help='Total capital for sizing')

    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    timeframe = args.timeframe
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Defaults based on timeframe
    if timeframe in ['1d', '3d', '1w', '5d']:
        approach = "Scalping/Day Trading"
        machine_type = "HYPE_MACHINE"
        position_size = "0.25% max"
        catalysts = """- **Intraday:** [Time] - [Event]
- **Short-term:** [Date] - [Event]"""
        review_date = "End of Day"
    elif timeframe in ['1m']:
        approach = "Swing Trading"
        machine_type = "HYPE_MACHINE"
        position_size = "0.25% max"
        catalysts = """- **Short-term:** [Date] - [Event]
- **Medium-term:** [Date] - [Event]"""
        review_date = "Weekly"
    elif timeframe in ['3m', '6m']:
        approach = "Position Trading"
        machine_type = "HYPE_MACHINE/MEAN_REVERSION"
        position_size = "0.5% max"
        catalysts = """- **Short-term:** [Date] - [Event]
- **Medium-term:** [Date] - [Event]
- **Long-term:** [Date] - [Event]"""
        review_date = "Monthly"
    else: # >1y or 1y
        approach = "Investment"
        machine_type = "EARNINGS_MACHINE"
        position_size = "1% max"
        catalysts = """- **Medium-term:** [Date] - [Event]
- **Long-term:** [Date] - [Event]"""
        review_date = "Quarterly"

    if args.capital:
        try:
            cap = float(args.capital)
            # Parse percentage from position_size string (rough heuristic)
            pct = float(position_size.split('%')[0])
            amt = cap * (pct / 100)
            position_size = f"{position_size} (${amt:,.2f})"
        except:
            pass

    content = TEMPLATE.format(
        ticker=ticker,
        timeframe=timeframe,
        machine_type=machine_type,
        approach=approach,
        position_size=position_size,
        catalysts=catalysts,
        date=date_str,
        review_date=review_date
    )
    
    root = get_project_root()
    output_dir = root / 'trading-plans' / ticker
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ticker}_{date_str.replace('-','_')}_{timeframe}.md"
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        f.write(content)
        
    print(f"Created template at: {output_path}")

if __name__ == '__main__':
    main()
