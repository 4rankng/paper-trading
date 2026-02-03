#!/usr/bin/env python3
"""
Create a new research document based on the standard template.
"""
import argparse
import os
from datetime import datetime
from pathlib import Path

TEMPLATE = """---
title: "{title}"
type: {type}
topic: {topic}
tags: [{tags}]
created: {date}
updated: {date}
related_stocks: [{tickers}]
related_sectors: [{sectors}]
importance: {importance}
status: active
machine_context: {machine}
intrinsic_weight: "{intrinsic}"
sentiment_momentum: "{sentiment}"
catalyst_type: {catalyst}
---

# {title}

## Executive Summary
(Key insights, investment implications, timeframe)

## Strategic Analysis
(Market dynamics, technology approach, competitive landscape)

## Sector/Topic Outlook
### Near-term (6-12 months)
- 

### Medium-term (1-3 years)
- 

### Long-term (3+ years)
- 

## Related Stocks Analysis
| Ticker | Analysis |
|--------|----------|
|        |          |

## Conclusion
(Key takeaways, investment perspective, risk/reward)

## References
- 
"""

def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".claude").exists():
             return parent
    return Path.cwd()

def to_kebab_case(s: str) -> str:
    return s.lower().replace(' ', '-')

def main():
    parser = argparse.ArgumentParser(description='Create a new research document.')
    parser.add_argument('--title', required=True, help='Document title')
    parser.add_argument('--type', required=True, choices=['sector', 'macro'], help='Type (sector/macro)')
    parser.add_argument('--topic', help='Topic (kebab-case, defaults to title)')
    parser.add_argument('--tickers', default='', help='Comma-separated related stocks')
    parser.add_argument('--sectors', default='', help='Comma-separated related sectors')
    parser.add_argument('--tags', default='', help='Comma-separated tags')
    parser.add_argument('--importance', default='medium', choices=['high', 'medium', 'low'], help='Importance')
    parser.add_argument('--machine', default='hype_play', choices=['hype_play', 'earnings_play', 'mean_reversion'], help='Machine context')
    parser.add_argument('--intrinsic', default='TBD', help='Intrinsic weight note')
    parser.add_argument('--sentiment', default='TBD', help='Sentiment/Momentum note')
    parser.add_argument('--catalyst', default='fundamental_earnings', help='Catalyst type')

    args = parser.parse_args()

    title = args.title
    doc_type = args.type
    topic = args.topic if args.topic else to_kebab_case(title)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Format lists
    tags = ', '.join([t.strip() for t in args.tags.split(',') if t.strip()])
    tickers = ', '.join([t.strip().upper() for t in args.tickers.split(',') if t.strip()])
    sectors = ', '.join([s.strip() for s in args.sectors.split(',') if s.strip()])

    content = TEMPLATE.format(
        title=title,
        type=doc_type,
        topic=topic,
        tags=tags,
        date=date_str,
        tickers=tickers,
        sectors=sectors,
        importance=args.importance,
        machine=args.machine,
        intrinsic=args.intrinsic,
        sentiment=args.sentiment,
        catalyst=args.catalyst
    )

    root = get_project_root()
    output_dir = root / 'research'
    output_dir.mkdir(exist_ok=True)
    
    filename = f"{doc_type}-{topic}-{date_str}.md"
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        f.write(content)
        
    print(f"Created research document at: {output_path}")

if __name__ == '__main__':
    main()
