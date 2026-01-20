#!/usr/bin/env python3
"""
Add central bank policy update.
"""

import argparse
import os
from datetime import datetime


BANK_NAMES = {
    "fed": "Federal Reserve",
    "ecb": "European Central Bank",
    "boj": "Bank of Japan",
    "pboc": "People's Bank of China",
}


def get_template(bank: str, month: str, decision: str, rate: str, statement: str) -> str:
    """Generate central bank update template."""
    bank_name = BANK_NAMES.get(bank.lower(), bank.upper())

    return f"""# {bank_name} Policy Update: {month.replace('_', '-')}

**Bank:** {bank_name}
**Month:** {month.replace('_', '-')}
**Decision:** {decision.upper() if decision else 'N/A'}
**Rate:** {rate if rate else 'N/A'}
**Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Policy Decision

**Action:** [{decision.upper() if decision else 'HOLD'}]

**New Rate Target:** [{rate if rate else 'X.XX - X.XX%'}]

**Vote Split:** [X-Y-Z] (if available)

## Statement Highlights

> [Key quotes from the policy statement]

{f"## Statement Summary\n\n{statement}\n" if statement else "## Statement Summary\n\n[Summary of the policy statement]\n"}

## Forward Guidance

[What the bank signaled about future policy moves]

## Market Reaction

### Immediate Market Response

- **Indices:** [SPY, QQQ reaction]
- **Yield Curve:** [2Y, 10Y response]
- **USD:** [DXY reaction if applicable]
- **Gold:** [Response]

### Volatility

- **VIX:** [Pre/post decision level]

## Economic Assessment

### Inflation

[Bank's view on inflation trajectory]

### Growth

[Bank's assessment of economic growth]

### Labor Market

[Bank's view on employment/jobs]

## Dot Plot / Projections (if available)

| Category | Current | Previous | Next Meeting Expected |
|----------|---------|----------|----------------------|
| Rate | X.XX% | X.XX% | [Hold/Hike/Cut] |
| GDP | X.X% | X.X% | X.X% |
| Unemployment | X.X% | X.X% | X.X% |
| Inflation | X.X% | X.X% | X.X% |

## Investment Implications

### Sectors Most Affected

1. **Financials:** [Rate sensitivity]
2. **Real Estate:** [Rate sensitivity]
3. **Technology:** [Growth vs value rotation]
4. **Consumer Discretionary:** [Economic sensitivity]

### Portfolio Adjustments

- [ ] Position sizing adjustments needed
- [ ] Sector rotation considerations
- [ ] Duration adjustments for fixed income

## Next Meeting

**Date:** [YYYY-MM-DD]
**Expected Action:** [Hold/Hike/Cut]
**Probability:** [XX%]

## Related Macro Files

- [Macro thesis](../../theses/macro_thesis_{month}.md)
- [Previous update](../{bank}_{get_prev_month(month)}.md)
"""


def get_prev_month(month: str) -> str:
    """Get previous month in YYYY_MM format."""
    year, m = month.split('_')
    y, m = int(year), int(m)
    if m == 1:
        m = 12
        y -= 1
    else:
        m -= 1
    return f"{y}_{m:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="Add central bank policy update"
    )
    parser.add_argument(
        "--bank",
        required=True,
        choices=["fed", "ecb", "boj", "pboc"],
        help="Central bank"
    )
    parser.add_argument("--month", required=True, help="Month in YYYY_MM format")
    parser.add_argument(
        "--decision",
        choices=["hold", "hike", "cut"],
        help="Policy decision"
    )
    parser.add_argument("--rate", help="Interest rate")
    parser.add_argument("--statement", help="Key statement summary")
    args = parser.parse_args()

    # Create directory
    macro_dir = "macro/central_banks"
    os.makedirs(macro_dir, exist_ok=True)

    # Generate filename
    filename = f"{args.bank}_{args.month}.md"
    filepath = os.path.join(macro_dir, filename)

    # Check if file exists
    if os.path.exists(filepath):
        print(f"Warning: {filepath} already exists.")

    # Write analysis
    with open(filepath, "w") as f:
        f.write(get_template(
            args.bank,
            args.month,
            args.decision or "",
            args.rate or "",
            args.statement or ""
        ))

    print(f"Created: {filepath}")


if __name__ == "__main__":
    main()
