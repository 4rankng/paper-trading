#!/usr/bin/env python3
"""
Create monthly macro thesis with economic overview and investment implications.
"""

import argparse
import os
from datetime import datetime


def get_template(month: str, stance: str = "NEUTRAL", risk_level: str = "MEDIUM") -> str:
    """Generate macro thesis template."""
    return f"""# Macro Thesis: {month.replace('_', '-')}

**Overall Stance:** {stance}
**Risk Level:** {risk_level}
**Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary

[2-3 sentence summary of current macro environment and investment implications]

## Key Economic Variables

| Variable | Current | Trend | Impact |
|----------|---------|-------|--------|
| GDP Growth (US) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| GDP Growth (China) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| GDP Growth (EU) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| Inflation (US CPI) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| Fed Funds Rate | X.XX% | ↗️/↘️/→ | HIGH/MED/LOW |
| Unemployment (US) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| 10Y Yield | X.XX% | ↗️/↘️/→ | HIGH/MED/LOW |

## Geopolitical Risks

### Active Risks

- **Risk 1:** [Description]
  - Impact: HIGH/MED/LOW
  - Sectors affected: [List sectors]
  - Timeline: [Short-term/Medium-term/Long-term]

- **Risk 2:** [Description]
  - Impact: HIGH/MED/LOW
  - Sectors affected: [List sectors]
  - Timeline: [Short-term/Medium-term/Long-term]

## Market Structure

| Factor | Status | Trend | Implication |
|--------|--------|-------|-------------|
| Liquidity | [Adequate/Tight] | ↗️/↘️/→ | [Description] |
| USD Strength | [Strong/Weak/Neutral] | ↗️/↘️/→ | [Description] |
| Credit Spreads | [Normal/Widening] | ↗️/↘️/→ | [Description] |
| Volatility (VIX) | [Low/Med/High] | ↗️/↘️/→ | [Description] |

## Sector Implications

| Sector | Tailwind | Headwind | Neutral | Notes |
|--------|----------|----------|---------|-------|
| Technology | | | X | [Notes] |
| Financials | | | X | [Notes] |
| Energy | | | X | [Notes] |
| Healthcare | | | X | [Notes] |
| Consumer Discretionary | | | X | [Notes] |
| Consumer Staples | | | X | [Notes] |
| Industrials | | | X | [Notes] |
| Real Estate | | | X | [Notes] |
| Utilities | | | X | [Notes] |
| Materials | | | X | [Notes] |
| Communication Services | | | X | [Notes] |

## Investment Implications

### Position Sizing

- **HIGH Risk:** Reduce position sizes by 50%, widen stops, delay new entries
- **MEDIUM Risk:** Standard allocation, normal stops
- **LOW Risk:** Full allocation, tighter stops possible

**Current:** {risk_level} risk environment

### Sector Preferences

**Favor:**
- [Sector 1]: [Reasoning]
- [Sector 2]: [Reasoning]

**Avoid/Reduce:**
- [Sector 1]: [Reasoning]
- [Sector 2]: [Reasoning]

### Key Watch Items

- [ ] [Event/Data release 1] - [Date]
- [ ] [Event/Data release 2] - [Date]
- [ ] [Event/Data release 3] - [Date]

## Central Bank Calendar

| Bank | Next Meeting | Expected Action | Impact |
|------|--------------|-----------------|--------|
| Fed | [Date] | [Hold/Hike/Cut] | [HIGH/MED/LOW] |
| ECB | [Date] | [Hold/Hike/Cut] | [HIGH/MED/LOW] |
| BOJ | [Date] | [Hold/Hike/Cut] | [HIGH/MED/LOW] |
| PBOC | [Date] | [Hold/Hike/Cut] | [HIGH/MED/LOW] |
"""


def main():
    parser = argparse.ArgumentParser(
        description="Create monthly macro thesis"
    )
    parser.add_argument("--month", required=True, help="Month in YYYY_MM format")
    parser.add_argument(
        "--stance",
        default="NEUTRAL",
        choices=["RISK-ON", "RISK-OFF", "NEUTRAL"],
        help="Overall market stance"
    )
    parser.add_argument(
        "--risk-level",
        default="MEDIUM",
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Risk level"
    )
    args = parser.parse_args()

    # Create directory
    macro_dir = "macro/theses"
    os.makedirs(macro_dir, exist_ok=True)

    # Generate file path
    filename = f"macro_thesis_{args.month}.md"
    filepath = os.path.join(macro_dir, filename)

    # Check if file exists
    if os.path.exists(filepath):
        print(f"Warning: {filepath} already exists. Use --force to overwrite.")

    # Write thesis
    with open(filepath, "w") as f:
        f.write(get_template(args.month, args.stance, args.risk_level))

    print(f"Created: {filepath}")
    print(f"Stance: {args.stance}, Risk Level: {args.risk_level}")


if __name__ == "__main__":
    main()
