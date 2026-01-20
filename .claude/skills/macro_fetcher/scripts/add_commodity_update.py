#!/usr/bin/env python3
"""
Add commodity price analysis.
"""

import argparse
import os
import re
from datetime import datetime
from urllib.parse import quote


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def get_template(commodity: str, month: str, trend: str, price: str) -> str:
    """Generate commodity update template."""
    trend_emoji = {
        "bullish": "↗️",
        "bearish": "↘️",
        "neutral": "→"
    }

    return f"""# {commodity.capitalize()} Analysis: {month.replace('_', '-')}

**Commodity:** {commodity.upper()}
**Current Price:** {price if price else 'N/A'}
**Trend:** {trend.upper()} {trend_emoji.get(trend.lower(), '→')}
**Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Price Action

### Current Level

**Price:** [{price if price else '$XX.XX'}]

**YTD:** [+X.X%]

**3M:** [+X.X%]

**12M:** [+X.X%]

### Technical Levels

- **Support:** $XX, $XX
- **Resistance:** $XX, $XX
- **52W High:** $XX
- **52W Low:** $XX

## Supply/Demand Dynamics

### Supply Side

[Supply factors affecting price]

### Demand Side

[Demand factors affecting price]

### Inventory Levels

[Current inventory status vs historical]

## Geopolitical Factors

- **Factor 1:** [Impact on price]
- **Factor 2:** [Impact on price]

## Correlations

| Asset | Correlation | Notes |
|-------|-------------|-------|
| USD | [Positive/Negative] | [Strength] |
| Equities | [Positive/Negative] | [Strength] |
| Inflation | [Positive/Negative] | [Strength] |

## Affected Sectors

### Direct Impact

1. **Sector 1:** [How price changes affect]
2. **Sector 2:** [How price changes affect]

### Indirect Impact

1. **Sector 1:** [Secondary effects]
2. **Sector 2:** [Secondary effects]

## Key Stocks

| Ticker | Exposure | Impact |
|--------|----------|--------|
| XXX | [Producer/Consumer] | [High/Med/Low] |
| XXX | [Producer/Consumer] | [High/Med/Low] |

## Outlook

### Scenarios

#### Bull Case (Price Higher)

[Conditions that would drive price up]

#### Bear Case (Price Lower)

[Conditions that would drive price down]

#### Base Case

[Most likely price path]

## Related Macro Files

- [Macro thesis](../../theses/macro_thesis_{month}.md)
- [Related commodities]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Add commodity price analysis"
    )
    parser.add_argument("--commodity", required=True,
                       help="Commodity name (oil/gold/copper/etc.)")
    parser.add_argument("--month", required=True, help="Month in YYYY_MM format")
    parser.add_argument(
        "--trend",
        choices=["bullish", "bearish", "neutral"],
        default="neutral",
        help="Price trend"
    )
    parser.add_argument("--price", help="Current price")
    args = parser.parse_args()

    # Create directory
    macro_dir = "macro/commodities"
    os.makedirs(macro_dir, exist_ok=True)

    # Generate filename
    slug = slugify(args.commodity)
    filename = f"{args.month}_{slug}.md"
    filepath = os.path.join(macro_dir, filename)

    # Check if file exists
    if os.path.exists(filepath):
        print(f"Warning: {filepath} already exists.")

    # Write analysis
    with open(filepath, "w") as f:
        f.write(get_template(args.commodity, args.month, args.trend, args.price or ""))

    print(f"Created: {filepath}")


if __name__ == "__main__":
    main()
