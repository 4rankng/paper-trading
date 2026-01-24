---
name: macro-fetcher
description: Fetch and manage macroeconomic analysis, geopolitical events, central bank policies, and global economic overview. ALWAYS use for ANY macro operations. Triggers: "macro update", "economic outlook", "fed policy", "geopolitical risk", "inflation data", "gdp growth", "global economy", "macro thesis". Use to maintain macro/ folder with weekly/monthly updates and event-driven analysis.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
  - WebSearch
  - mcp__web-reader__webReader
  - mcp__web-search-prime__webSearchPrime
---

# Macro Fetcher Skill

Fetch and manage macroeconomic analysis that influences equity market decisions.

**MANDATORY UPDATE RULE:** Any LLM agent that discovers new macroeconomic information, geopolitical developments, central bank policy changes, or market-relevant analysis MUST immediately update the appropriate file in the `macro/` folder. This is not optional - if you find it, you document it.

## Content Categories

**1. Global Economic Overview**
- GDP growth rates by major economies (US, China, EU, Japan, Emerging Markets)
- Inflation trends (CPI, PPI) and central bank policy stance
- Interest rate environment and yield curve dynamics
- Employment and labor market conditions

**2. Geopolitical Tensions**
- Trade wars, tariffs, and economic sanctions
- Regional conflicts affecting supply chains/commodities
- Diplomatic relations between major powers (US-China, Russia-Europe, etc.)
- Election outcomes and policy implications

**3. Market Structure Issues**
- Liquidity conditions and credit spreads
- Currency fluctuations (USD strength/weakness)
- Commodity price shocks (oil, metals, agriculture)
- Systemic risks (banking stress, real estate bubbles)

**4. Sector-Specific Macro Trends**
- Regulatory changes affecting specific industries
- Technological disruptions with macro implications
- ESG policy shifts and climate-related regulations

## Usage in Investment Decisions

When evaluating any investment:
1. **Check current macro stance** by reading `macro/theses/macro_thesis_YYYY_MM.md`
2. **Consider sector-specific headwinds/tailwinds** from macro events
3. **Factor macro conditions into:**
   - Position sizing (reduce exposure in high macro risk periods)
   - Entry timing (delay entries during elevated macro uncertainty)
   - Thesis validation (macro shifts can invalidate sector theses)

## Maintenance

- **Weekly**: Update macro folder with key economic developments
- **Monthly**: Comprehensive macro thesis update
- **Event-driven**: Immediate updates for major geopolitical or policy events

## Quick Start

```bash
# List existing macro analysis
ls -lt macro/theses/

# Create monthly macro thesis
python .claude/skills/macro_fetcher/scripts/create_macro_thesis.py --month 2026_01

# Add geopolitical event analysis
python .claude/skills/macro_fetcher/scripts/add_geopolitical_event.py \
  --topic "US-China Trade" \
  --impact "HIGH" \
  --sectors "technology,consumer"

# Add central bank update
python .claude/skills/macro_fetcher/scripts/add_central_bank_update.py \
  --bank fed \
  --month 2026_01
```

## Common Workflows

### Monthly Macro Thesis Update
```bash
# STEP 1: Gather economic data (WebSearch, financial sources)
# - GDP growth rates
# - Inflation (CPI, PPI)
# - Interest rates, yield curve
# - Employment data

# STEP 2: Create comprehensive thesis
python .claude/skills/macro_fetcher/scripts/create_macro_thesis.py --month 2026_01

# STEP 3: Save to macro/theses/macro_thesis_YYYY_MM.md
```

### Event-Driven Analysis (Geopolitical, Policy)
```bash
# Add analysis for major events
python .claude/skills/macro_fetcher/scripts/add_geopolitical_event.py \
  --topic "Topic Name" \
  --date YYYY-MM-DD \
  --impact "HIGH|MEDIUM|LOW" \
  --sectors "affected,sectors"
```

### Central Bank Policy Tracking
```bash
# Fed, ECB, BOJ, PBOC policy updates
python .claude/skills/macro_fetcher/scripts/add_central_bank_update.py \
  --bank fed \
  --month 2026_01 \
  --decision "hold|hike|cut" \
  --rate X.XX
```

## File Structure

**Location**: `macro/{category}/{filename}.md`

```
macro/
├── theses/
│   └── macro_thesis_YYYY_MM.md    # Overall macro stance
├── overview/
│   └── YYYY_MM.md                  # Monthly global economic summary
├── geopolitical/
│   └── YYYY_MM_topic.md           # Event analysis
├── central_banks/
│   ├── fed_YYYY_MM.md             # Federal Reserve
│   ├── ecb_YYYY_MM.md             # European Central Bank
│   ├── boj_YYYY_MM.md             # Bank of Japan
│   └── pboc_YYYY_MM.md            # People's Bank of China
└── commodities/
    └── YYYY_MM_commodity.md       # Oil, gold, etc.
```

## Macro Thesis Template

**File**: `macro/theses/macro_thesis_YYYY_MM.md`

```markdown
# Macro Thesis: YYYY-MM

**Overall Stance:** RISK-ON / RISK-OFF / NEUTRAL
**Risk Level:** HIGH / MEDIUM / LOW
**Updated:** YYYY-MM-DD

## Executive Summary

[2-3 sentence summary of current macro environment and investment implications]

## Key Variables

| Variable | Current | Trend | Impact |
|----------|---------|-------|--------|
| GDP Growth (US) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| Inflation (CPI) | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |
| Fed Funds Rate | X.XX% | ↗️/↘️/→ | HIGH/MED/LOW |
| Unemployment | X.X% | ↗️/↘️/→ | HIGH/MED/LOW |

## Geopolitical Risks

- **Risk 1:** [Description] - Impact: [HIGH/MED/LOW]
- **Risk 2:** [Description] - Impact: [HIGH/MED/LOW]

## Sector Implications

| Sector | Tailwind | Headwind | Neutral |
|--------|----------|----------|---------|
| Technology | | | X |
| Financials | X | | |
| Energy | | X | |

## Investment Implications

**Position Sizing:**
- HIGH risk: Reduce sizes by 50%
- MEDIUM risk: Standard allocation
- LOW risk: Full allocation

**Sector Preferences:** [Sectors to favor/avoid]

**Key Watch Items:** [Events/data to monitor]
```

## Advanced

**Complete scripts reference**: See [scripts.md](references/scripts.md) for all parameters and usage examples.
