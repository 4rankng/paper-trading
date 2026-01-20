#!/usr/bin/env python3
"""
Add analysis for geopolitical events affecting markets.
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


def get_template(topic: str, impact: str, sectors: str, date: str) -> str:
    """Generate geopolitical event template."""
    sector_list = ", ".join(sectors.split(",")) if sectors else "None specified"

    return f"""# {topic}

**Impact Level:** {impact}
**Date:** {date}
**Affected Sectors:** {sector_list}
**Created:** {datetime.now().strftime('%Y-%m-%d')}

## Event Summary

[Brief description of the geopolitical event]

## Market Impact

### Immediate Impact

- **Indices:** [SPY, QQQ, IWM reaction]
- **Sectors:** [Sector-specific reactions]
- **Safe Havens:** [Gold, Treasuries reaction]

### Expected Duration

- [ ] Short-term (days-weeks)
- [ ] Medium-term (1-3 months)
- [ ] Long-term (3+ months)

## Affected Sectors

### {sectors.split(',')[0] if sectors else 'Technology'}

**Impact:** [Positive/Negative/Mixed]

**Key Companies:**
- [Company 1]: [Exposure level]
- [Company 2]: [Exposure level]

**Thesis Implications:**
- [For existing holdings]: [Considerations]
- [For new entries]: [Adjustments needed]

## Scenarios

### Bull Case (De-escalation)

[What happens if situation improves]

### Bear Case (Escalation)

[What happens if situation worsens]

### Base Case (Status Quo)

[Most likely outcome]

## Monitoring Checklist

- [ ] [News source 1]
- [ ] [News source 2]
- [ ] [Government announcement source]
- [ ] [Key indicator to watch]

## Related Macro Files

- [Macro thesis](../../theses/macro_thesis_YYYY_MM.md)
- [Related events]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Add geopolitical event analysis"
    )
    parser.add_argument("--topic", required=True, help="Event topic name")
    parser.add_argument(
        "--impact",
        required=True,
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Impact level"
    )
    parser.add_argument("--sectors", help="Comma-separated affected sectors")
    parser.add_argument("--date", default=datetime.now().strftime('%Y-%m-%d'),
                       help="Event date (YYYY-MM-DD)")
    args = parser.parse_args()

    # Create directory
    macro_dir = "macro/geopolitical"
    os.makedirs(macro_dir, exist_ok=True)

    # Generate slug and filename
    slug = slugify(args.topic)
    year_month = args.date[:7].replace('-', '_')
    filename = f"{year_month}_{slug}.md"
    filepath = os.path.join(macro_dir, filename)

    # Check if file exists
    if os.path.exists(filepath):
        print(f"Warning: {filepath} already exists.")

    # Write analysis
    with open(filepath, "w") as f:
        f.write(get_template(args.topic, args.impact, args.sectors or "", args.date))

    print(f"Created: {filepath}")


if __name__ == "__main__":
    main()
