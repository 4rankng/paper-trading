# Research File Template

**Location:** `research/{type}-{topic}-{date}.md`

**File Naming:**
- Type: sector, macro
- Topic: kebab-case (e.g., robotaxi-sector)
- Date: YYYY-MM-DD

**Example:** `research/sector-robotaxi-2025-01-17.md`

---

## Required Frontmatter

Every research file MUST include this frontmatter:

```yaml
---
title: "Topic Analysis"
type: [sector|macro]
topic: topic-name
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
related_stocks: [TICKER1, TICKER2]
related_sectors: [sector1, sector2]
importance: [high|medium|low]
status: [active|archived|superseded]
machine_context: [hype_play|earnings_play|mean_reversion]
intrinsic_weight: "Fair value vs price"
sentiment_momentum: "High/Low/Overheated"
catalyst_type: [fundamental_earnings|sentiment_hype]
---
```

## Content Structure

### Executive Summary
- Key insights (2-3 paragraphs)
- Investment implications
- Timeframe

### Strategic Analysis
- Market dynamics
- Technology approach
- Competitive landscape
- Investment insights

### Sector/Topic Outlook
- Near-term (6-12 months)
- Medium-term (1-3 years)
- Long-term (3+ years)

### Related Stocks Analysis
- Quick comparison table
- Top picks analysis
- Investment recommendations

### Conclusion
- Key takeaways
- Investment perspective
- Risk/reward assessment

## Retrieval

Search by:
- Tags (most efficient)
- `related_stocks` field
- `status: active` and `importance: high` filters

## Best Practices

1. Use specific, searchable tags
2. Keep related_stocks updated
3. Archive outdated research (status: archived)
4. Cross-reference related research files
5. Include sources/references at end
