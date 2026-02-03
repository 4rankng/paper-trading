#!/usr/bin/env python3
"""
Quality Compound Scorer - Wealth Building System

For: Proven businesses, stable compounders, dividend growers
Goal: 15-30% CAGR with low volatility
Focus: Fundamentals, moats, valuation, execution consistency

GATEKEEPERS (Must pass ALL to be scored):
  - Market Cap: > $2B (Avoids micro-cap volatility)
  - Operating Cash Flow: Positive for last 3 years
  - Interest Coverage: > 4x (No debt spirals)

Reads from ./analytics/{TICKER}/:
- {TICKER}_technical_analysis.md
- {TICKER}_investment_thesis.md
- {TICKER}_fundamental_analysis.md

Output: JSON with scores 0-100 for each component + overall quality_score
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "skills" / "analytics_generator" / "scripts"

# Quality Compound Scoring weights (UPDATED)
WEIGHTS = {
    "moat": 0.30,           # Competitive advantage durability (was 25%)
    "fundamentals": 0.25,   # Financial health, margins, ROE (was 30%)
    "growth_quality": 0.20, # Sustainable growth, not explosive
    "valuation": 0.15,      # Paying reasonable price
    "management": 0.10,     # Capital allocation, execution (was "execution")
}

# Quality thresholds
QUALITY_THRESHOLDS = [
    (85, "Exceptional", "STRONG BUY"),
    (75, "Excellent", "BUY"),
    (65, "Good", "BUY"),
    (55, "Above Average", "ADD"),
    (45, "Average", "HOLD"),
    (35, "Below Average", "REDUCE"),
    (0, "Poor", "AVOID"),
]

# Quality Classifications
QUALITY_TYPES = {
    "CAPITAL_CANNIBAL": {
        "description": "Aggressive share reducer",
        "criteria": "Buybacks reduce float by >3% annually",
        "examples": "AutoZone, Apple",
        "exit_trigger": "P/E expands 50% above historical average OR buyback program paused"
    },
    "THE_FRANCHISE": {
        "description": "Pricing power dominant",
        "criteria": "Dominant market share, raises prices above inflation",
        "examples": "Microsoft, Moody's",
        "exit_trigger": "Market share decline >2% OR pricing power erodes"
    },
    "THE_STALWART": {
        "description": "Steady Eddie",
        "criteria": "Lower growth (8-12%) but high dividend + safety",
        "examples": "J&J, PepsiCo",
        "exit_trigger": "Dividend cut OR fundamental degradation"
    }
}

# Gatekeepers - Must pass ALL to be scored
GATEKEEPERS = {
    "market_cap": {
        "threshold": 2000,  # $2B
        "field": "market_cap",
        "reason": "Micro-cap volatility risk"
    },
    "ocf_positive": {
        "threshold": 3,  # 3 years
        "field": "ocf_years_positive",
        "reason": "Negative operating cash flow"
    },
    "interest_coverage": {
        "threshold": 4.0,  # 4x
        "field": "interest_coverage",
        "reason": "Debt spiral risk"
    }
}

REQUIRED_ANALYTICS = ["technical", "thesis", "fundamental"]

ANALYTICS_FILES = {
    "thesis": ["{ticker}_investment_thesis.md"],
    "technical": ["{ticker}_technical_analysis.md", "technical.md"],
    "fundamental": ["{ticker}_fundamental_analysis.md", "fundamental.md"],
}


@dataclass
class ScoreComponent:
    """Individual score component with reasoning."""
    score: int
    reasoning: str
    evidence: List[str] = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


@dataclass
class QualityScore:
    """Complete quality compound scoring result."""
    ticker: str
    name: str
    quality_score: float
    compound_potential: str  # Expected annual return range
    volatility_risk: str     # Low, Medium, High
    quality_type: str        # CAPITAL_CANNIBAL, THE_FRANCHISE, THE_STALWART, or None
    components: Dict[str, ScoreComponent]
    classification: str
    recommended_action: str
    calculated_at: str
    fair_value: float = None
    margin_of_safety: str = None
    gatekeepers_passed: bool = True
    gatekeeper_failures: List[str] = None
    exit_triggers: List[str] = None


def get_analytics_file(ticker: str, file_type: str) -> Optional[str]:
    """Read analytics file from ./analytics/{TICKER}/ directory."""
    if file_type not in ANALYTICS_FILES:
        return None

    folder = PROJECT_ROOT / "analytics" / ticker.upper()

    for filename_template in ANALYTICS_FILES[file_type]:
        filename = filename_template.format(ticker=ticker.upper())
        file_path = folder / filename

        if file_path.exists():
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                return file_path.read_text(encoding='latin-1', errors='replace')
    return None


def check_gatekeepers(ticker: str, fundamental_text: str, thesis_text: str) -> Tuple[bool, List[str]]:
    """Check if stock passes all gatekeepers BEFORE scoring.

    Returns:
        (passed, failures) tuple
    """
    failures = []
    text = (fundamental_text + " " + thesis_text).lower()

    # Gatekeeper 1: Market Cap > $2B
    # Look for market cap info in text
    import re
    mc_match = re.search(r'market cap.*?\$?([\d.]+)\s*(b|m|billion)', text)
    if mc_match:
        value = float(mc_match.group(1))
        unit = mc_match.group(2).lower()
        if unit in ['m', 'million']:
            value_millions = value
        else:  # billion
            value_millions = value * 1000

        if value_millions < 2000:
            failures.append(f"Market Cap ${value_millions/1000:.1f}B < $2B threshold")
    else:
        # Can't verify - assume pass but note uncertainty
        pass

    # Gatekeeper 2: Operating Cash Flow positive for 3 years
    if 'negative operating cash flow' in text or 'negative ocf' in text:
        failures.append("Operating Cash Flow negative")
    if 'burning cash' in text or 'cash burn' in text:
        failures.append("Cash burn detected")

    # Gatekeeper 3: Interest Coverage > 4x
    ic_match = re.search(r'interest coverage.*?([\d.]+)', text)
    if ic_match:
        ic = float(ic_match.group(1))
        if ic < 4.0:
            failures.append(f"Interest Coverage {ic}x < 4x threshold")
    else:
        # Check for debt/EBITDA as proxy
        de_match = re.search(r'debt.*?ebitda.*?([\d.]+)', text)
        if de_match:
            de = float(de_match.group(1))
            if de > 4.0:
                failures.append(f"Debt/EBITDA {de}x > 4x threshold")

    return len(failures) == 0, failures


def determine_quality_type(thesis_text: str, fundamental_text: str) -> Optional[str]:
    """Determine quality classification: CAPITAL_CANNIBAL, THE_FRANCHISE, or THE_STALWART."""
    text = (thesis_text + " " + fundamental_text).lower()

    # CAPITAL_CANNIBAL: Aggressive buybacks reducing float
    buyback_signals = [
        'buyback', 'share repurchase', 'repurchase program', 'reducing share count',
        'share reduction', 'buying back shares'
    ]
    buyback_score = sum(1 for s in buyback_signals if s in text)

    # THE_FRANCHISE: Pricing power, dominant market share
    franchise_signals = [
        'pricing power', 'dominant market share', 'market leader',
        'competitive advantage', 'wide moat', 'price increases'
    ]
    franchise_score = sum(1 for s in franchise_signals if s in text)

    # THE_STALWART: Dividend, stable, lower growth
    stalwart_signals = [
        'dividend', 'dividend yield', 'dividend growth', 'stable',
        'steady', 'defensive', 'low volatility'
    ]
    stalwart_score = sum(1 for s in stalwart_signals if s in text)

    # Determine type based on highest score
    scores = {
        "CAPITAL_CANNIBAL": buyback_score,
        "THE_FRANCHISE": franchise_score,
        "THE_STALWART": stalwart_score
    }

    max_score = max(scores.values())
    if max_score >= 2:  # Need at least 2 signals
        return max(scores, key=scores.get)

    return None


def get_exit_triggers(quality_type: str) -> List[str]:
    """Get exit triggers based on quality type."""
    if quality_type and quality_type in QUALITY_TYPES:
        return [QUALITY_TYPES[quality_type]["exit_trigger"]]

    # Default exit triggers for unclassified quality compounders
    return [
        "Valuation: P/E expands 50% above historical average",
        "Fundamental: ROE declines below 12%",
        "Thesis: Competitive moat shows signs of erosion",
        "Technical: Break below 200-day MA on high volume (confirmation only)"
    ]


def build_quality_prompt(ticker: str, name: str, context: Dict) -> str:
    """Build the prompt for LLM quality compound scoring."""

    prompt = f"""You are an expert equity research analyst specializing in **quality compounder** identification.

**Stock:** {ticker} ({name})
**Current Price:** ${context.get('price', 'N/A')}

**Technical Analysis:**
```
{context.get('technical_analysis', 'No data')[:4000]}
```

**Investment Thesis:**
```
{context.get('thesis', 'No data')[:3000]}
```

**Fundamental Analysis:**
```
{context.get('fundamental', 'No data')[:2000]}
```

---

## QUALITY COMPOUNDER SCORING SYSTEM

**Goal:** Identify businesses that can compound wealth at 15-30% annually with low volatility.

**UPDATED WEIGHTS:**
- Moat & Power (30%): Competitive advantage durability
- Fundamentals (25%): Financial health, margins, ROE
- Growth Quality (20%): Sustainable growth (15-30%), not explosive
- Valuation (15%): Paying reasonable price
- Management/Capital Allocation (10%): Shareholder-friendly decisions

---

## 1. Competitive Moat (30% weight)

**90-100:** Wide moat with multiple defenses
- Network effects (value scales with users)
- Switching costs >6 months to change vendor
- Regulatory licenses/monopoly-like position
- Intangible assets (brands, patents, IP) with 10+ year protection
- Cost advantage unassailable (scale, proprietary tech, location)

**75-89:** Narrow moat with clear advantage
- Strong brand recognition
- Customer loyalty (high retention rates)
- Some switching costs
- Moderate cost advantage
- Protected niche market

**60-74:** Emerging moat
- Building competitive position
- Early signs of customer lock-in
- Differentiation but not yet proven

**40-59:** No sustainable advantage
- Commodity product/service
- Price competition primary differentiator
- Low barriers to entry
- Customer churn high

**Below 40:** Moat erosion or non-existent

---

## 2. Fundamentals (25% weight)

**90-100:** Exceptional financials
- Gross margin >60% (software) or >30% (hardware/retail)
- Operating margin >20%
- ROE >20% or ROIC >15%
- Debt/Equity <50% or Net Cash position
- Free cash flow positive and growing
- Current ratio >1.5

**75-89:** Strong financials
- Gross margin >50% (software) or >25% (hardware)
- Operating margin >15%
- ROE >15%
- Manageable debt
- Positive FCF
- Adequate liquidity

**60-74:** Good financials
- Gross margin >40% or >20%
- Operating margin >10%
- ROE >10%
- Reasonable debt load
- Breaking even on FCF

**40-59:** Average/poor financials
- Margins declining or below industry
- ROE <10%
- High debt burden
- FCF negative

**Below 40:** Financial distress risks

---

## 3. Growth Quality (20% weight)

**IMPORTANT:** For quality compounders, we want SUSTAINABLE growth, not explosive spikes.

**90-100:** Ideal growth profile
- 15-30% revenue growth (sustainable, not requiring massive capex)
- Growth driven by market share gain + industry growth
- Same store growth > new store growth (retail)
- Growth funding internally (not dilution)

**75-89:** Strong sustainable growth
- 10-25% revenue growth
- Consistent growth over 5+ years
- Balanced organic + inorganic

**60-74:** Moderate growth
- 5-15% growth
- Some volatility but positive trend
- May require moderate capital

**40-59:** Low or volatile growth
- <5% growth or negative
- Inconsistent (boom/bust)
- Capital-intensive growth

**Below 40:** Stagnant or declining

---

## 4. Valuation (15% weight)

**90-100:** Deep value
- P/E <12 for 15%+ growers
- P/E <15 for 10-15% growers
- EV/EBITDA <8
- Price below fair value by >30%

**75-89:** Attractive valuation
- P/E 12-18 for growers
- EV/EBITDA 8-12
- 10-30% below fair value

**60-74:** Fair value
- P/E 18-25 for quality growers
- EV/EBITDA 12-15
- Trading near fair value

**40-59:** Expensive
- P/E >30 for moderate growers
- P/E >40 for any company
- >30% above fair value

**Below 40:** Significantly overvalued

**Note:** For exceptional compounders (90+ moat score), valuation can be stretched by 20%.

---

## 5. Management & Capital Allocation (10% weight)

**90-100:** Excellent capital allocation
- Shareholder-friendly (dividends, buybacks, accretive M&A)
- R&D spending creates value (ROI measurable)
- Management tenure >5 years with proven track record
- Clear communication, guidance mostly met or exceeded

**75-89:** Good capital allocation
- Generally makes smart capital decisions
- Some buybacks/dividends
- Management stable

**60-74:** Adequate execution
- Mixed capital allocation record
- Strategy shifts occasionally
- Management newer but competent

**40-59:** Poor execution
- Value-destroying acquisitions
- Dilution common
- Strategy inconsistency
- Misses guidance frequently

**Below 40:** Capital destruction

---

## COMPOUND POTENTIAL CLASSIFICATION

Based on scores, classify compound potential:

| Quality Score | Compound Potential | Volatility Risk | Time Horizon |
|---------------|-------------------|-----------------|--------------|
| 85-100 | 25-30% CAGR | Low | 5-10 years |
| 75-84 | 20-25% CAGR | Low-Medium | 5-10 years |
| 65-74 | 15-20% CAGR | Medium | 3-7 years |
| 55-64 | 10-15% CAGR | Medium | 2-5 years |
| 45-54 | 5-10% CAGR | Medium-High | 1-3 years |
| Below 45 | <5% or negative | High | Avoid |

---

## QUALITY TYPE CLASSIFICATION

Determine which type of quality compounder:

**CAPITAL_CANNIBAL** (Share Reducer)
- Aggressive buybacks reduce float by >3% annually
- Examples: AutoZone, Apple
- Exit: P/E expands 50% above historical OR buyback program paused

**THE_FRANCHISE** (Pricing Power)
- Dominant market share, raises prices above inflation
- Examples: Microsoft, Moody's
- Exit: Market share decline >2% OR pricing power erodes

**THE_STALWART** (Steady Eddie)
- Lower growth (8-12%) but high dividend + safety
- Examples: J&J, PepsiCo
- Exit: Dividend cut OR fundamental degradation

---

## MARGIN OF SAFETY CALCULATION

Calculate fair value using:
- DCF with 8-10% discount rate for quality names
- P/E multiple at 20-25x for 15% growers, 25-30x for 20%+ growers
- EV/EBITDA 12-15x for quality compounders

Margin of Safety = (Fair Value - Current Price) / Fair Value

---

## OUTPUT FORMAT (JSON only):

```json
{{
  "moat": {{"score": 85, "reasoning": "Network effects + switching costs", "evidence": ["95% customer retention", "3+ year contracts"]}},
  "fundamentals": {{"score": 78, "reasoning": "Strong margins and ROE", "evidence": ["GM 72%", "ROE 22%", "Net cash position"]}},
  "growth_quality": {{"score": 72, "reasoning": "Sustainable 18% growth", "evidence": ["5 year avg 17%", "Same-store growth 12%"]}},
  "valuation": {{"score": 65, "reasoning": "Fair value for quality", "evidence": ["P/E 22x for 18% grower", "5% below DCF value"]}},
  "management": {{"score": 80, "reasoning": "Shareholder friendly capital allocation", "evidence": ["10% buyback yield", "R&D ROI 18%"]}},
  "fair_value": {{"price": 150.00, "method": "DCF 9% discount, 22x P/E multiple", "margin_of_safety_pct": 12}},
  "quality_type": "CAPITAL_CANNIBAL"
}}
```

Provide ONLY the JSON. No markdown, no explanation.
"""
    return prompt


def call_claude_for_scoring(prompt: str) -> Optional[Dict]:
    """Call Claude API for scoring."""
    try:
        from anthropic import Anthropic

        client = Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        content = message.content[0].text
        return parse_json_response(content)

    except ImportError:
        try:
            result = subprocess.run(
                ["claude", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return parse_json_response(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"  Warning: Could not use Anthropic API or claude CLI: {e}", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: LLM scoring failed: {e}", file=sys.stderr)

    return None


def parse_json_response(response: str) -> Optional[Dict]:
    """Parse JSON from LLM response."""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None


def calculate_quality_score(scores: Dict) -> float:
    """Calculate weighted quality score."""
    total = sum(
        scores.get(component, {}).get("score", 50) * weight
        for component, weight in WEIGHTS.items()
    )
    return round(total, 1)


def get_compound_potential(score: float) -> tuple:
    """Get compound potential and volatility risk from score."""
    if score >= 85:
        return "25-30% CAGR", "Low"
    elif score >= 75:
        return "20-25% CAGR", "Low-Medium"
    elif score >= 65:
        return "15-20% CAGR", "Medium"
    elif score >= 55:
        return "10-15% CAGR", "Medium"
    elif score >= 45:
        return "5-10% CAGR", "Medium-High"
    else:
        return "<5% or negative", "High"


def get_classification(score: float) -> tuple:
    """Get classification and action from score."""
    for threshold, classification, action in QUALITY_THRESHOLDS:
        if score >= threshold:
            return classification, action
    return "Poor", "AVOID"


def score_quality_compound(ticker: str, name: str = "N/A") -> Optional[QualityScore]:
    """Score a stock for quality compound potential."""
    print(f"Scoring {ticker} for Quality Compound potential...", flush=True)

    # Gather analytics
    thesis_text = get_analytics_file(ticker, "thesis") or ""
    context = {
        "thesis": thesis_text,
        "fundamental": get_analytics_file(ticker, "fundamental"),
        "technical_analysis": get_analytics_file(ticker, "technical"),
    }

    # Check gatekeepers FIRST
    gatekeepers_passed, gatekeeper_failures = check_gatekeepers(ticker, context.get("fundamental", ""), thesis_text)

    if not gatekeepers_passed:
        print(f"  {ticker} failed gatekeepers: {', '.join(gatekeeper_failures)}", file=sys.stderr)
        # Still return a score but mark gatekeepers as failed

    # Get price from watchlist
    watchlist_path = PROJECT_ROOT / "watchlist.json"
    if watchlist_path.exists():
        try:
            with open(watchlist_path) as f:
                watchlist = json.load(f)
            for entry in watchlist:
                if entry.get("ticker") == ticker.upper():
                    context["price"] = entry.get("price", "N/A")
                    break
        except (json.JSONDecodeError, IOError):
            pass

    # Check we have required data
    if not all(context.get(k) for k in ["thesis", "fundamental", "technical_analysis"]):
        print(f"  Error: Missing required analytics for {ticker}", file=sys.stderr)
        return None

    # Build prompt and score
    prompt = build_quality_prompt(ticker, name, context)
    scores = call_claude_for_scoring(prompt)

    if not scores:
        print(f"  Error: LLM scoring failed for {ticker}", file=sys.stderr)
        return None

    # Calculate quality score
    quality_score = calculate_quality_score(scores)

    # Get classifications
    classification, recommended_action = get_classification(quality_score)
    compound_potential, volatility_risk = get_compound_potential(quality_score)

    # Extract fair value
    fair_value_data = scores.pop("fair_value", {})
    fair_value = fair_value_data.get("price") if isinstance(fair_value_data, dict) else None
    margin_of_safety = fair_value_data.get("margin_of_safety_pct") if isinstance(fair_value_data, dict) else None

    # Determine quality type
    quality_type = scores.pop("quality_type", None)
    if not quality_type:
        quality_type = determine_quality_type(thesis_text, context.get("fundamental", ""))

    # Get exit triggers
    exit_triggers = get_exit_triggers(quality_type)

    # Convert to ScoreComponent objects
    components = {}
    for k, v in scores.items():
        if isinstance(v, dict) and "score" in v:
            components[k] = ScoreComponent(
                score=v.get("score", 50),
                reasoning=v.get("reasoning", ""),
                evidence=v.get("evidence", [])
            )

    return QualityScore(
        ticker=ticker.upper(),
        name=name,
        quality_score=quality_score,
        compound_potential=compound_potential,
        volatility_risk=volatility_risk,
        quality_type=quality_type,
        components=components,
        classification=classification,
        recommended_action=recommended_action,
        calculated_at=datetime.now().isoformat(),
        fair_value=fair_value,
        margin_of_safety=margin_of_safety,
        gatekeepers_passed=gatekeepers_passed,
        gatekeeper_failures=gatekeeper_failures,
        exit_triggers=exit_triggers
    )


def format_console_output(results: list) -> None:
    """Print results in mobile-friendly table format."""
    print(f"\n{'Ticker':<8} {'Quality':<10} {'Moat':<8} {'Fund':<8} {'Growth':<8} {'Val':<8} {'Mgmt':<8} {'Action':<10}")
    print("-" * 100)

    for r in results:
        comps = r.get('components', {})
        moat = comps.get('moat', {}).get('score', 50)
        fund = comps.get('fundamentals', {}).get('score', 50)
        growth = comps.get('growth_quality', {}).get('score', 50)
        val = comps.get('valuation', {}).get('score', 50)
        mgmt = comps.get('management', {}).get('score', 50)
        action = r.get('recommended_action', 'N/A')

        score = r['quality_score']
        potential = r.get('compound_potential', '')
        q_type = r.get('quality_type', 'N/A')[:15]

        print(f"{r['ticker']:<8} {score:<10.1f} {moat:<8} {fund:<8} {growth:<8} {val:<8} {mgmt:<8} {action:<10}")

        if r.get('fair_value'):
            print(f"         Type: {q_type} | Fair Value: ${r['fair_value']} | MoS: {r.get('margin_of_safety', 'N/A')}% | Expected: {potential}")

        if not r.get('gatekeepers_passed', True):
            print(f"         ⚠️ GATEKEEPER FAIL: {', '.join(r.get('gatekeeper_failures', []))}")

        if r.get('exit_triggers'):
            print(f"         Exit: {r['exit_triggers'][0][:60]}...")


def quality_score_to_dict(score: QualityScore) -> Dict:
    """Convert QualityScore to dict for JSON serialization."""
    return {
        "ticker": score.ticker,
        "name": score.name,
        "quality_score": score.quality_score,
        "compound_potential": score.compound_potential,
        "volatility_risk": score.volatility_risk,
        "quality_type": score.quality_type,
        "classification": score.classification,
        "recommended_action": score.recommended_action,
        "components": {
            k: {"score": v.score, "reasoning": v.reasoning, "evidence": v.evidence}
            for k, v in (score.components or {}).items()
        },
        "fair_value": score.fair_value,
        "margin_of_safety": score.margin_of_safety,
        "gatekeepers_passed": score.gatekeepers_passed,
        "gatekeeper_failures": score.gatekeeper_failures,
        "exit_triggers": score.exit_triggers,
        "calculated_at": score.calculated_at
    }


def load_watchlist() -> Dict:
    """Load watchlist.json as {ticker: entry} dict."""
    watchlist_path = PROJECT_ROOT / "watchlist.json"
    if not watchlist_path.exists():
        return {}

    try:
        with open(watchlist_path) as f:
            watchlist = json.load(f)
        return {entry.get("ticker", "").upper(): entry for entry in watchlist}
    except (json.JSONDecodeError, IOError):
        return {}


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Quality Compound Scorer - Identify wealth-building compounders"
    )
    parser.add_argument("--ticker", help="Single ticker to score")
    parser.add_argument("--tickers", help="Comma-separated tickers")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--min-score", type=float, default=0, help="Minimum score to display")

    args = parser.parse_args()

    # Load watchlist for ticker names
    watchlist = load_watchlist()

    # Get tickers to process
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    elif args.ticker:
        tickers = [args.ticker.upper()]
    else:
        parser.error("Must specify --ticker or --tickers")

    # Score each stock
    results = []
    failed = []
    for ticker in tickers:
        entry = watchlist.get(ticker.upper(), {})
        name = entry.get("name", "N/A")
        result = score_quality_compound(ticker, name)

        if result:
            result_dict = quality_score_to_dict(result)
            if result_dict["quality_score"] >= args.min_score:
                results.append(result_dict)
        else:
            failed.append(ticker)

    if failed:
        print(f"\nFailed to score: {', '.join(failed)}", flush=True)

    # Sort by quality score descending
    results.sort(key=lambda x: x["quality_score"], reverse=True)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved {len(results)} results to {args.output}")
    else:
        format_console_output(results)


if __name__ == "__main__":
    main()
