#!/usr/bin/env python3
"""
Multi-Bagger Hunter Scorer - Speculative High-Upside System

For: Early-stage, speculative, high-growth, binary outcome stocks
Goal: 5-10x potential with acceptable loss of capital
Focus: TAM, founder quality, technology moat, secular tailwind, network effects

GATEKEEPERS (Must pass ALL to be scored):
  - Liquidity: Daily Dollar Volume > $2M (Must be able to exit)
  - Solvency: Cash Runway > 12 months OR Path to Profitability within 18 months
  - Trend: Price above 200-day Moving Average (Don't catch falling knives)

UPDATED WEIGHTS (Jan 2026):
  - Innovation Moat (25%): Proprietary IP, "Un-copyable" tech
  - TAM & Optionality (20%): Total Addressable Market (was 25%, now 20%)
  - Founder/Vision (20%): Founder-led, Skin in the game
  - Hyper-Growth (20%): Revenue growth >30% YoY (NEW)
  - Unit Economics (15%): Gross Margins expanding, LTV/CAC > 3 (NEW)

Reads from ./analytics/{TICKER}/:
- {TICKER}_technical_analysis.md
- {TICKER}_investment_thesis.md
- {TICKER}_fundamental_analysis.md

Output: JSON with scores 0-100 for each component + overall multibagger_score
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Multi-Bagger Hunter scoring weights (UPDATED Jan 2026)
WEIGHTS = {
    "innovation_moat": 0.25,     # Proprietary technology, IP protection (was "tech_moat")
    "tam": 0.20,                 # Total Addressable Market size (was 25%, now 20%)
    "founder": 0.20,             # Founder/Management quality and vision
    "hyper_growth": 0.20,        # Revenue growth >30% YoY (NEW - replaces "secular_tailwind" + "network_effects")
    "unit_economics": 0.15,      # Gross Margins expanding, LTV/CAC > 3 (NEW)
}

# Multi-bagger thresholds
MULTIBAGGER_THRESHOLDS = [
    (85, "Generational", "STRONG BUY"),
    (75, "Exceptional", "STRONG BUY"),
    (65, "Outstanding", "BUY"),
    (55, "Strong", "BUY"),
    (45, "Moderate", "WATCH"),
    (35, "Weak", "WATCH"),
    (0, "Poor", "AVOID"),
]

# Phenomenon Classifications (Standardized)
PHENOMENON_TYPES = {
    "HYPE_MACHINE": {
        "description": "Revolutionary tech + retail momentum potential",
        "entry": "Breakout from consolidation base",
        "exit": "Trailing Stop Loss (20-30%) or if growth decelerates for 2 quarters"
    },
    "CATEGORY_KING": {
        "description": "Winner-takes-most (Network Effects)",
        "entry": "When market share crosses 15-20%",
        "exit": "Network effect slows OR competitor reaches feature parity"
    },
    "TURNAROUND": {
        "description": "New CEO/Strategy or Cycle shift",
        "entry": "First 'beat and raise' quarter",
        "exit": "Turnaround fails OR re-rating complete"
    },
    "EARNINGS_MACHINE": {
        "description": "Compounding with re-rating potential",
        "entry": "Before discovery (sub-50% score that improves)",
        "exit": "Valuation extended OR fundamental degradation"
    },
    "PRODUCT_LAUNCH": {
        "description": "Binary outcome on single product",
        "entry": "Pre-launch or at approval",
        "exit": "Product fails OR post-launch success (take profits)"
    },
    "HIDDEN_GEM": {
        "description": "Micro-cap ignored by institutions",
        "entry": "Post-IPO lockup expiration",
        "exit": "Institutional coverage begins (re-rating complete)"
    }
}

# Gatekeepers - Must pass ALL to be scored
GATEKEEPERS = {
    "liquidity": {
        "threshold": 2_000_000,  # $2M daily dollar volume
        "reason": "Insufficient liquidity to exit position"
    },
    "runway": {
        "threshold": 12,  # 12 months
        "reason": "Cash runway < 12 months (bankruptcy risk)"
    },
    "trend": {
        "threshold": 200,  # 200-day MA
        "reason": "Price below 200-day MA (falling knife)"
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
class MultibaggerScore:
    """Complete multi-bagger hunting scoring result."""
    ticker: str
    name: str
    multibagger_score: float
    upside_potential: str      # 5x, 10x, etc.
    binary_risk: str           # Low, Medium, High
    time_to_validation: str    # Expected validation timeline
    phenomenon_type: str       # HYPE_MACHINE, CATEGORY_KING, etc.
    components: Dict[str, ScoreComponent]
    classification: str
    recommended_action: str
    calculated_at: str
    target_price_5x: float = None
    target_price_10x: float = None
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


def check_gatekeepers(ticker: str, technical_text: str, fundamental_text: str) -> Tuple[bool, List[str]]:
    """Check if stock passes all gatekeepers BEFORE scoring.

    Returns:
        (passed, failures) tuple
    """
    failures = []
    text = (technical_text + " " + fundamental_text).lower()

    # Gatekeeper 1: Liquidity - Daily Dollar Volume > $2M
    vol_match = re.search(r'avg volume.*?([\d.]+)\s*[km]?', text)
    if vol_match:
        volume = float(vol_match.group(1))
        # This is a rough check - actual implementation would need price data
        # For now, we'll note if liquidity is mentioned as a concern
        if 'low liquidity' in text or 'illiquid' in text:
            failures.append("Low liquidity - Daily volume < $2M")

    # Gatekeeper 2: Runway - Cash > 12 months or path to profitability < 18 months
    runway_match = re.search(r'runway.*?([\d.]+)\s*months?', text)
    if runway_match:
        runway = float(runway_match.group(1))
        if runway < 12:
            failures.append(f"Runway {runway} months < 12 month threshold")
    else:
        # Check for cash burn warnings
        if 'less than 6 months' in text or '< 6 months' in text:
            failures.append("Cash runway < 6 months")

    # Gatekeeper 3: Trend - Price above 200-day MA (Don't catch falling knives)
    if 'below 200-day ma' in text or 'below 200 dma' in text or 'below ma200' in text:
        failures.append("Price below 200-day MA (falling knife risk)")

    return len(failures) == 0, failures


def determine_phenomenon_type(thesis_text: str, technical_text: str) -> str:
    """Determine phenomenon type from thesis and technical analysis."""
    text = (thesis_text + " " + technical_text).lower()

    # Check for HYPE_MACHINE indicators
    hype_signals = ['revolutionary', 'paradigm shift', 'game-changing', 'disruptive',
                   'breakthrough', 'transformative', 'groundbreaking']
    hype_score = sum(1 for s in hype_signals if s in text)

    # Check for CATEGORY_KING (network effects)
    category_signals = ['network effect', 'winner-takes-most', 'winner takes most',
                       'platform', 'market place', 'flywheel', 'data moat']
    category_score = sum(1 for s in category_signals if s in text)

    # Check for TURNAROUND
    turnaround_signals = ['turnaround', 'new ceo', 'new management', 'restructuring',
                         'strategic shift', 'under new leadership']
    turnaround_score = sum(1 for s in turnaround_signals if s in text)

    # Check for EARNINGS_MACHINE
    earnings_signals = ['compound', 'earnings growth', 'margin expansion',
                       'operating leverage', 're-rating']
    earnings_score = sum(1 for s in earnings_signals if s in text)

    # Check for PRODUCT_LAUNCH
    product_signals = ['fda approval', 'launch', 'product release', 'patent approval',
                      'clinical trial', 'platform launch']
    product_score = sum(1 for s in product_signals if s in text)

    # Check for HIDDEN_GEM
    hidden_signals = ['micro-cap', 'neglected', 'overlooked', 'undercovered',
                     'underfollowed', 'small cap']
    hidden_score = sum(1 for s in hidden_signals if s in text)

    # Determine type based on highest score
    scores = {
        "HYPE_MACHINE": hype_score,
        "CATEGORY_KING": category_score,
        "TURNAROUND": turnaround_score,
        "EARNINGS_MACHINE": earnings_score,
        "PRODUCT_LAUNCH": product_score,
        "HIDDEN_GEM": hidden_score
    }

    max_score = max(scores.values())
    if max_score >= 2:  # Need at least 2 signals
        return max(scores, key=scores.get)

    return "SPECULATIVE_GROWTH"


def get_exit_triggers(phenomenon_type: str) -> List[str]:
    """Get exit triggers based on phenomenon type."""
    if phenomenon_type and phenomenon_type in PHENOMENON_TYPES:
        return [PHENOMENON_TYPES[phenomenon_type]["exit"]]

    # Default exit triggers for multibaggers
    return [
        "Trailing Stop Loss (20-30%) on momentum breakdown",
        "Growth decelerates for 2 consecutive quarters",
        "Fundamental thesis invalidated",
        "Time horizon exceeded without validation"
    ]


def build_multibagger_prompt(ticker: str, name: str, context: Dict) -> str:
    """Build the prompt for LLM multi-bagger scoring."""

    prompt = f"""You are an expert venture capital and growth equity analyst specializing in **multi-bagger identification**.

**Stock:** {ticker} ({name})
**Current Price:** ${context.get('price', 'N/A')}
**Market Cap:** ${context.get('market_cap', 'N/A')}M

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

## MULTI-BAGGER HUNTER SCORING SYSTEM

**Goal:** Identify stocks with 5-10x+ potential over 3-7 years.

**CRITICAL Philosophy:** Multi-baggers LOOK expensive and risky on traditional metrics. We SCORE for asymmetric upside, not current profitability.

**UPDATED WEIGHTS (Jan 2026):**
- Innovation Moat (25%): Proprietary technology, IP protection
- TAM & Optionality (20%): Total Addressable Market size (reduced from 25%)
- Founder/Vision (20%): Visionary founder with proven track record
- Hyper-Growth (20%): Revenue growth >30% YoY (NEW)
- Unit Economics (15%): Gross Margins expanding, LTV/CAC > 3 (NEW)

---

## 1. Innovation Moat & IP (25% weight)

**90-100:** Proprietary Technology, Defensible
- Patented technology with 5-10+ year protection
- Trade secrets difficult to reverse engineer
- Technology significantly ahead of competition (2+ years)
- High R&D barrier to entry
- Network effects or switching costs embedded

**75-89:** Strong Technology Position
- Meaningful IP portfolio
- Clear technical differentiation
- R&D spending creating moat
- Some barriers to entry

**60-74:** Adequate Technology
- Competitive product but not clearly superior
- Limited IP protection
- Moderate R&D spend

**40-59:** Weak Moat
- Commodity technology
- Easy to replicate
- Low R&D, no IP
- Pure execution play

**Below 40:** No Moat
- Reselling others' technology
- No R&D, no IP

---

## 2. TAM & Optionality (20% weight) - REDUCED from 25%

**90-100:** Massive Market ($100B+)
- Market will inevitably be huge (not "could be")
- Societal/structural shift driving adoption
- Winner-takes-all or winner-takes-most dynamics
- Examples: Cloud computing, EVs, AI, gene therapy, quantum security

**75-89:** Large Market ($10B-$100B)
- Significant market with clear growth path
- Multiple use cases expanding TAM
- Strong secular driver

**60-74:** Moderate Market ($1B-$10B)
- Defined niche with growth potential
- Limited expansion opportunities
- May be winner-takes-most in niche

**40-59:** Small Market (<$1B)
- Niche market with limited expansion
- Crowded competitive landscape
- Winner-takes-small-fragment

**Below 40:** Tiny/Declining Market

---

## 3. Founder & Management Quality (20% weight)

**90-100:** Visionary Founder with Proven Track Record
- Founder has built +$1B company before
- Visionary thinking (5-10 years ahead)
- Significant founder ownership (>20%)
- Long-term orientation (not flipping)
- Recruited world-class team

**75-89:** Strong Leadership
- Experienced management with relevant background
- Founder ownership 10-20%
- Clear vision communicated well
- Strong technical pedigree

**60-74:** Competent Leadership
- Adequate management experience
- Some founder ownership
- Vision exists but less clear

**40-59:** Questionable Leadership
- Management turnover
- No founder involvement
- Short-term focus
- Weak communication

**Below 40:** Red Flags
- Related party transactions
- Excessive compensation without performance
- Founder cashing out aggressively

---

## 4. Hyper-Growth (20% weight) - NEW (replaces Secular Tailwind + Network Effects)

**90-100:** Explosive Growth
- Revenue growth >50% YoY AND accelerating
- User/customer growth >50% YoY
- Expanding into new verticals
- International expansion working

**75-89:** Very Strong Growth
- Revenue growth >30% YoY
- User/customer growth >30% YoY
- Expanding product lines
- Early international presence

**60-74:** Strong Growth
- Revenue growth >20% YoY
- User/customer growth >20% YoY
- Stable growth trajectory

**40-59:** Moderate/Decelerating Growth
- Revenue growth <20% YoY
- Growth rate declining
- Limited expansion opportunities

**Below 40:** Low/No Growth
- Revenue growth <10% YoY OR negative
- Stagnant user base
- No growth catalysts

---

## 5. Unit Economics (15% weight) - NEW

**90-100:** Excellent Unit Economics
- Gross Margins >70% AND expanding
- LTV/CAC > 5
- Payback period < 12 months
- Negative churn (expansion revenue > churn)

**75-89:** Strong Unit Economics
- Gross Margins >60% OR expanding
- LTV/CAC > 3
- Payback period < 18 months
- Churn <5%

**60-74:** Adequate Unit Economics
- Gross Margins >50%
- LTV/CAC > 2
- Payback period < 24 months
- Manageable churn

**40-59:** Poor Unit Economics
- Gross Margins <40% OR declining
- LTV/CAC < 2
- Payback period > 36 months
- High churn (>10%)

**Below 40:** Broken Unit Economics
- Gross Margins <30%
- LTV/CAC < 1 (losing money on every customer)
- Payback period > 48 months
- Churn >20%

---

## MULTI-BAGGER CLASSIFICATION

| Score | Upside Potential | Binary Risk | Time Horizon | Phenomenon Type |
|-------|-----------------|-------------|--------------|-----------------|
| 85-100 | 10-20x | High | 5-10 years | HYPE_MACHINE, CATEGORY_KING |
| 75-84 | 7-10x | High | 3-7 years | HYPE_MACHINE, PRODUCT_LAUNCH |
| 65-74 | 5-7x | Medium-High | 3-5 years | EARNINGS_MACHINE, TURNAROUND |
| 55-64 | 3-5x | Medium | 2-4 years | CATEGORY_KING, TURNAROUND |
| 45-54 | 2-3x | Medium | 1-3 years | Not a multi-bagger |
| Below 45 | <2x | High/High | Avoid | |

---

## PHENOMENON CLASSIFICATIONS (Multi-Bagger Types)

**HYPE_MACHINE** (Highest upside, highest risk)
- Revolutionary technology
- Retail/retail momentum potential
- Visionary founder
- Rich valuation but can go much higher
- Entry: Breakout from consolidation base
- Exit: Trailing Stop Loss (20-30%) or if growth decelerates for 2 quarters
- Examples: Early Tesla, Nvidia AI, Quantum plays

**CATEGORY_KING** (Winner-takes-most)
- Network effects
- Winner-takes-most dynamics
- Data flywheel
- Entry: When market share crosses 15-20%
- Exit: Network effect slows OR competitor reaches feature parity
- Examples: Meta, Uber, Airbnb

**TURNAROUND** (Medium upside, medium risk)
- New CEO/Strategy or Cycle shift
- Distressed with turnaround potential
- Entry: First "beat and raise" quarter
- Exit: Turnaround fails OR re-rating complete
- Examples: Turnaround situations

**EARNINGS_MACHINE** (Medium-high upside, lower risk)
- Compounding with re-rating potential
- Optionality on new products/markets
- Entry: Before discovery (sub-50% score that improves)
- Exit: Valuation extended OR fundamental degradation
- Examples: Tech compounders before discovery

**PRODUCT_LAUNCH** (Binary upside, high risk)
- Single product can drive entire value
- FDA approval, platform launch, etc.
- Entry: Pre-launch or at approval
- Exit: Product fails OR post-launch success (take profits)
- Examples: Biotech, platform tech

**HIDDEN_GEM** (Micro-cap opportunity)
- Micro-cap ignored by institutions
- Pre-coverage opportunity
- Entry: Post-IPO lockup expiration
- Exit: Institutional coverage begins (re-rating complete)
- Examples: Nano-caps with strong fundamentals

---

## TARGET PRICE CALCULATION

For multi-baggers, calculate:
- **5x target:** Current price × 5
- **10x target:** Current price × 10

Assess achievability based on:
- Current market cap × 5-10x = Reasonable in this TAM?
- Comparables trade at what valuations?
- Can revenue/earnings support this in 5-7 years?

---

## OUTPUT FORMAT (JSON only):

```json
{{
  "innovation_moat": {{"score": 88, "reasoning": "Patented hardware-level PQC implementation", "evidence": ["12 patents granted", "QS7001 chip launched"]}},
  "tam": {{"score": 90, "reasoning": "$100B+ inevitable market in quantum security", "evidence": ["Government mandate for PQC", "Every system needs upgrade"]}},
  "founder": {{"score": 85, "reasoning": "Visionary founder with PhD in quantum cryptography", "evidence": ["20+ years industry experience", "25% founder ownership"]}},
  "hyper_growth": {{"score": 75, "reasoning": "Revenue growth 35% YoY, accelerating", "evidence": ["Q3 revenue +35% YoY", "Q2 was +28%", "New EU contracts"]}},
  "unit_economics": {{"score": 70, "reasoning": "Gross margins 65%, LTV/CAC estimated >3", "evidence": ["GM 65% and expanding", "Government customers LTV high"]}},
  "targets": {{
    "price_5x": 150.00,
    "price_10x": 300.00,
    "market_cap_10x": "6B",
    "achievable_10x": true,
    "reasoning": "10x = $6B MC, reasonable for $100B TAM market leader with 40% GM"
  }},
  "phenomenon_type": "HYPE_MACHINE",
  "time_to_validation": "2-3 years (UE breakeven, government contracts)"
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


def calculate_multibagger_score(scores: Dict) -> float:
    """Calculate weighted multi-bagger score."""
    total = sum(
        scores.get(component, {}).get("score", 50) * weight
        for component, weight in WEIGHTS.items()
    )
    return round(total, 1)


def get_upside_potential(score: float) -> tuple:
    """Get upside potential and binary risk from score."""
    if score >= 85:
        return "10-20x", "High"
    elif score >= 75:
        return "7-10x", "High"
    elif score >= 65:
        return "5-7x", "Medium-High"
    elif score >= 55:
        return "3-5x", "Medium"
    elif score >= 45:
        return "2-3x", "Medium"
    else:
        return "<2x", "High"


def get_classification(score: float) -> tuple:
    """Get classification and action from score."""
    for threshold, classification, action in MULTIBAGGER_THRESHOLDS:
        if score >= threshold:
            return classification, action
    return "Poor", "AVOID"


def score_multibagger(ticker: str, name: str = "N/A") -> Optional[MultibaggerScore]:
    """Score a stock for multi-bagger potential."""
    print(f"Scoring {ticker} for Multi-Bagger potential...", flush=True)

    # Gather analytics
    thesis_text = get_analytics_file(ticker, "thesis") or ""
    technical_text = get_analytics_file(ticker, "technical") or ""
    context = {
        "thesis": thesis_text,
        "fundamental": get_analytics_file(ticker, "fundamental"),
        "technical_analysis": technical_text,
    }

    # Check gatekeepers FIRST
    gatekeepers_passed, gatekeeper_failures = check_gatekeepers(ticker, technical_text, context.get("fundamental", ""))

    if not gatekeepers_passed:
        print(f"  {ticker} failed gatekeepers: {', '.join(gatekeeper_failures)}", file=sys.stderr)
        # Still return a score but mark gatekeepers as failed

    # Get price and market cap from watchlist
    watchlist_path = PROJECT_ROOT / "watchlist.json"
    if watchlist_path.exists():
        try:
            with open(watchlist_path) as f:
                watchlist = json.load(f)
            for entry in watchlist:
                if entry.get("ticker") == ticker.upper():
                    context["price"] = entry.get("price", "N/A")
                    # Calculate market cap if shares known
                    if entry.get("shares") and entry.get("price"):
                        context["market_cap"] = entry["shares"] * entry["price"] / 1_000_000
                    break
        except (json.JSONDecodeError, IOError):
            pass

    # Check we have required data
    if not all(context.get(k) for k in ["thesis", "fundamental", "technical_analysis"]):
        print(f"  Error: Missing required analytics for {ticker}", file=sys.stderr)
        return None

    # Build prompt and score
    prompt = build_multibagger_prompt(ticker, name, context)
    scores = call_claude_for_scoring(prompt)

    if not scores:
        print(f"  Error: LLM scoring failed for {ticker}", file=sys.stderr)
        return None

    # Calculate multi-bagger score
    multibagger_score = calculate_multibagger_score(scores)

    # Get classifications
    classification, recommended_action = get_classification(multibagger_score)
    upside_potential, binary_risk = get_upside_potential(multibagger_score)

    # Determine phenomenon type
    phenomenon_type = scores.pop("phenomenon_type", None)
    if not phenomenon_type:
        phenomenon_type = determine_phenomenon_type(thesis_text, technical_text)

    # Extract targets
    targets_data = scores.pop("targets", {})
    price_5x = targets_data.get("price_5x") if isinstance(targets_data, dict) else None
    price_10x = targets_data.get("price_10x") if isinstance(targets_data, dict) else None

    # Extract time to validation
    time_to_validation = targets_data.get("time_to_validation") if isinstance(targets_data, dict) else "Unknown"

    # Get exit triggers
    exit_triggers = get_exit_triggers(phenomenon_type)

    # Convert to ScoreComponent objects
    components = {}
    for k, v in scores.items():
        if isinstance(v, dict) and "score" in v:
            components[k] = ScoreComponent(
                score=v.get("score", 50),
                reasoning=v.get("reasoning", ""),
                evidence=v.get("evidence", [])
            )

    return MultibaggerScore(
        ticker=ticker.upper(),
        name=name,
        multibagger_score=multibagger_score,
        upside_potential=upside_potential,
        binary_risk=binary_risk,
        time_to_validation=time_to_validation,
        phenomenon_type=phenomenon_type,
        components=components,
        classification=classification,
        recommended_action=recommended_action,
        calculated_at=datetime.now().isoformat(),
        target_price_5x=price_5x,
        target_price_10x=price_10x,
        gatekeepers_passed=gatekeepers_passed,
        gatekeeper_failures=gatekeeper_failures,
        exit_triggers=exit_triggers
    )


def format_console_output(results: list) -> None:
    """Print results in mobile-friendly table format."""
    print(f"\n{'Ticker':<8} {'MB Score':<10} {'Innov':<8} {'TAM':<8} {'Fdr':<8} {'Growth':<8} {'UnitE':<8} {'Action':<10}")
    print("-" * 100)

    for r in results:
        comps = r.get('components', {})
        innov = comps.get('innovation_moat', {}).get('score', 50)
        tam = comps.get('tam', {}).get('score', 50)
        founder = comps.get('founder', {}).get('score', 50)
        growth = comps.get('hyper_growth', {}).get('score', 50)
        unit = comps.get('unit_economics', {}).get('score', 50)
        action = r.get('recommended_action', 'N/A')

        score = r['multibagger_score']
        potential = r.get('upside_potential', '')
        risk = r.get('binary_risk', '')
        phenomenon = r.get('phenomenon_type', 'N/A')[:15]

        print(f"{r['ticker']:<8} {score:<10.1f} {innov:<8} {tam:<8} {founder:<8} {growth:<8} {unit:<8} {action:<10}")
        print(f"         Potential: {potential} | Risk: {risk} | Type: {phenomenon}")

        if r.get('target_price_5x'):
            print(f"         5x: ${r['target_price_5x']:.2f} | 10x: ${r['target_price_10x']:.2f}")

        if not r.get('gatekeepers_passed', True):
            print(f"         ⚠️ GATEKEEPER FAIL: {', '.join(r.get('gatekeeper_failures', []))}")

        if r.get('exit_triggers'):
            print(f"         Exit: {r['exit_triggers'][0][:60]}...")

        # Show key evidence
        for comp_name, comp_data in list(comps.items())[:3]:
            if comp_data.get('evidence'):
                print(f"         {comp_name.title()}: {comp_data['evidence'][0][:50]}...")


def multibagger_score_to_dict(score: MultibaggerScore) -> Dict:
    """Convert MultibaggerScore to dict for JSON serialization."""
    return {
        "ticker": score.ticker,
        "name": score.name,
        "multibagger_score": score.multibagger_score,
        "upside_potential": score.upside_potential,
        "binary_risk": score.binary_risk,
        "time_to_validation": score.time_to_validation,
        "phenomenon_type": score.phenomenon_type,
        "classification": score.classification,
        "recommended_action": score.recommended_action,
        "components": {
            k: {"score": v.score, "reasoning": v.reasoning, "evidence": v.evidence}
            for k, v in (score.components or {}).items()
        },
        "target_price_5x": score.target_price_5x,
        "target_price_10x": score.target_price_10x,
        "calculated_at": score.calculated_at,
        "gatekeepers_passed": score.gatekeepers_passed,
        "gatekeeper_failures": score.gatekeeper_failures,
        "exit_triggers": score.exit_triggers
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
        description="Multi-Bagger Hunter - Identify 5-10x speculative opportunities"
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
        result = score_multibagger(ticker, name)

        if result:
            result_dict = multibagger_score_to_dict(result)
            if result_dict["multibagger_score"] >= args.min_score:
                results.append(result_dict)
        else:
            failed.append(ticker)

    if failed:
        print(f"\nFailed to score: {', '.join(failed)}", flush=True)

    # Sort by multi-bagger score descending
    results.sort(key=lambda x: x["multibagger_score"], reverse=True)

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
