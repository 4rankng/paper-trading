#!/usr/bin/env python3
"""
Two-Stage Stock Scoring System

Stage 1: STRATEGIC SCORE (0-100) - Determines IF the asset is worth owning
  - Thesis Strength (40%): Catalysts, moat, narrative
  - Fundamental Health (30%): Margins, ROE, debt, growth
  - Upside Potential (30%): Expected Return based on Fair Value

Stage 2: TACTICAL MODIFIER - Determines WHEN to execute (timing only)
  - Technical Health: Trend, momentum, volume
  - Risk/Reward: Entry setup quality

KEY PRINCIPLE: Technical weakness does NOT reduce Strategic Score.
A great company with a bad chart = Opportunity (DCA), not Avoid.

Reads from ./analytics/{TICKER}/:
- {TICKER}_technical_analysis.md
- {TICKER}_investment_thesis.md
- {TICKER}_fundamental_analysis.md

Output: JSON with strategic_score, tactical_score, entry_strategy
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

# Stage 1: Strategic Scoring weights (Buy Decision)
STRATEGIC_WEIGHTS = {
    "thesis": 0.40,        # Catalysts, moat, narrative
    "fundamental": 0.30,   # Financial health, margins, growth
    "upside": 0.30,        # Fair value upside %
}

# Stage 2: Tactical weights (Entry Timing - NOT part of buy score)
TACTICAL_WEIGHTS = {
    "technical": 0.60,     # Trend, momentum, volume
    "risk_reward": 0.40,   # Entry setup quality
}

# Strategic score thresholds
STRATEGIC_THRESHOLDS = [
    (80, "Generational", "STRONG BUY"),
    (65, "Investable", "BUY"),
    (50, "Watchlist", "WATCH"),
    (0, "Avoid", "AVOID"),
]

# Required analytics files
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
class StockScore:
    """Complete two-stage stock scoring result."""
    ticker: str
    name: str
    strategic_score: float      # Stage 1: What to buy
    tactical_score: float       # Stage 2: When to buy
    classification: str         # Generational, Investable, Watchlist, Avoid
    recommended_action: str     # BUY, WATCH, AVOID
    entry_strategy: str         # How to execute based on both scores
    components: Dict[str, ScoreComponent]
    calculated_at: str
    fair_value: float = None
    fair_value_method: str = None
    fair_value_confidence: str = None
    thesis_status: str = None   # INTACT, CRACKING, BROKEN


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


def get_price_data(ticker: str) -> Optional[Dict]:
    """Get current price data from watchlist."""
    watchlist_path = PROJECT_ROOT / "watchlist.json"
    if not watchlist_path.exists():
        return None

    try:
        with open(watchlist_path) as f:
            watchlist = json.load(f)
        for entry in watchlist:
            if entry.get("ticker") == ticker.upper():
                return {
                    "price": entry.get("price"),
                    "rr": entry.get("rr"),
                    "stop": entry.get("stop"),
                    "exit": entry.get("exit"),
                }
    except (json.JSONDecodeError, IOError):
        pass
    return None


def build_scoring_prompt(ticker: str, name: str, context: Dict) -> str:
    """Build the prompt for LLM scoring with fair value estimation."""

    current_price = context.get('price', 'N/A')

    prompt = f"""You are an expert equity research analyst. Score the following stock using the TWO-STAGE system.

**Stock:** {ticker} ({name})
**Current Price:** ${current_price}

**Technical Analysis:**
```
{context.get('technical_analysis', 'No technical analysis data available.')[:4000]}
```

**Investment Thesis:**
```
{context.get('thesis', 'No thesis file available.')[:3000]}
```

**Fundamental Analysis:**
```
{context.get('fundamental', 'No fundamental data available.')[:2000]}
```

---

# TWO-STAGE SCORING SYSTEM

## STAGE 1: STRATEGIC SCORE (What to Buy)

Determines IF the asset is worth owning. Focus on business quality and upside.

### 1. Thesis Strength (40% weight)

Base Score: 50. Adjust based on criteria below.

| Criteria | Adjustment | Cap |
|----------|------------|-----|
| Catalyst Density | +5 per confirmed catalyst with date set | Max +20 |
| Moat Quality | +20 (Wide/Deep), +10 (Narrow), 0 (None) | Max +20 |
| Conviction Level | +10 (High), 0 (Medium), -10 (Low/Speculative) | Max +10 |
| Sector Trend | +10 (Secular Tailwind), -10 (Headwind) | Max +10 |
| Thesis Status | -20 if Thesis BROKEN or invalidated | Min -20 |

**Score Ranges:**
- 90-100: Multiple near-term catalysts (<90 days), wide moat, secular tailwind
- 75-89: Clear catalysts, defensible moat, supportive sector
- 60-74: Some catalysts, moderate moat
- 40-59: Weak catalysts, no moat, headwinds
- Below 40: No clear path, thesis broken

### 2. Fundamental Health (30% weight)

Base Score: 50. Assess business health.

| Metric | Bullish (+10 each) | Bearish (-10 each) |
|--------|-------------------|-------------------|
| Growth | Revenue Growth > 25% | Revenue Decline (YoY) |
| Margins | Gross Margin > 50% OR Expanding | Margins Compressing |
| Profitability | Rule of 40 (Growth + FCF% > 40) | Cash Burn < 6mo Runway |
| Returns | ROIC > 15% | ROIC < WACC |
| Solvency | Net Cash Positive | Debt/EBITDA > 4x |

**Score Ranges:**
- 90-100: Excellent margins (20%+), strong ROE (15%+), low debt, high growth
- 75-89: Good margins (10%+), decent ROE, manageable debt
- 60-74: Average fundamentals, some concerns
- 40-59: Weak margins, high debt, or declining growth
- Below 40: Poor fundamentals, burning cash, accounting risks

### 3. Upside Potential (30% weight)

Based on conservative Fair Value (FV) modeling.

**Score Formula:** `min(100, Upside % × 2)`

| Exp Return | Calculation | Score |
|------------|-------------|-------|
| > 50% | Score 100 | Asymmetric Opportunity |
| 25-50% | Score 75-90 | Strong Compounder |
| 10-25% | Score 50-74 | Market Performer |
| < 10% | Score < 40 | Overvalued/Fairly Valued |

**Fair Value Methods:**
- **DCF**: For companies with clear FCF projections (8-12% discount rate)
- **P/E Multiple**: For stable earners (compare to sector avg, growth rate)
- **EV/EBITDA**: For capital-intensive businesses
- **Probability-Weighted**: For speculative names (bull/base/bear scenarios)

**Fair Value Guidelines:**
- Growth stocks (25%+ EPS growth): 25-35x P/E
- Quality compounders (15-25% growth): 20-30x P/E
- Stable earners (10-15% growth): 15-20x P/E
- Value/cyclical: 10-15x P/E or 8-12x EBITDA

---

## STAGE 2: TACTICAL SCORE (When to Buy)

Determines entry timing and strategy. Does NOT affect Strategic Score.

### 1. Technical Health (60% weight)

From technical analysis: Trend, momentum, volume indicators.

- 90-100: Strong breakout, ideal entry zone, momentum confirmation
- 75-89: Bullish trend, pullback to support, good entry
- 60-74: Mildly bullish, can enter but wait for better setup
- 40-59: Neutral, sideways, wait
- Below 40: Bearish, avoid entry (WAIT for better entry, not AVOID)

### 2. Risk/Reward Setup (40% weight)

| R:R Ratio | Score |
|-----------|-------|
| ≥ 3.0 | 100 |
| ≥ 2.0 | 80 |
| ≥ 1.5 | 60 |
| ≥ 1.0 | 40 |
| < 1.0 | 20 |

---

# DECISION MATRIX

Combine Strategic Score with Tactical Setup to determine action:

| Strategic Score | Classification | Action |
|----------------|---------------|--------|
| 80-100 | Generational | BUY. If Technicals weak, start scaling in (DCA) |
| 65-79 | Investable | BUY. Standard position size |
| 50-64 | Watchlist | WAIT. Only buy if Technicals are A+ |
| < 50 | Avoid | IGNORE. Fundamental thesis too weak |

**Entry Strategy Logic:**

1. **Strategic ≥ 65 + Tactical ≥ 70**: MOMENTUM ENTRY (Breakout)
2. **Strategic ≥ 80 + Tactical < 40**: AGGRESSIVE ACCUMULATION (Divergence = Opportunity)
3. **Strategic 65-79 + Tactical 40-69**: DCA / LIMIT ORDERS
4. **Strategic 50-64 + Tactical ≥ 80**: MOMENTUM PLAY (Lower conviction)
5. **Strategic < 50**: AVOID regardless of technicals

---

# OUTPUT FORMAT (JSON only)

```json
{{
  "thesis": {{"score": 85, "reasoning": "3 catalyst dates set, wide moat, secular tailwind", "evidence": ["Q1 data readout", "Patent protection", "AI tailwind"]}},
  "fundamental": {{"score": 70, "reasoning": "Strong margins but high debt", "evidence": ["GM 65%", "ROE 18%", "Debt/EBITDA 3.2x"]}},
  "upside": {{"score": 90, "reasoning": "60% upside to fair value", "evidence": ["FV $550 vs current $340", "DCF 9% discount"]}},
  "technical": {{"score": 45, "reasoning": "Consolidating below 200-day MA", "evidence": ["Price < MA200", "RSI 48", "Volume below avg"]}},
  "risk_reward": {{"score": 80, "reasoning": "R:R 2.5:1 to nearest resistance", "evidence": ["Entry $340, Target $490, Stop $280"]}},
  "fair_value": {{
    "price": 550.00,
    "method": "DCF with 9% discount rate, 28x P/E multiple",
    "confidence": "High",
    "reasoning": "Based on $45B FCF, 28x P/E implies $550. Current price $340 = 62% upside"
  }},
  "thesis_status": "INTACT"
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


def calculate_strategic_score(scores: Dict) -> float:
    """Calculate Stage 1 Strategic Score (Buy Decision)."""
    total = sum(
        scores.get(component, {}).get("score", 50) * weight
        for component, weight in STRATEGIC_WEIGHTS.items()
    )
    return round(total, 1)


def calculate_tactical_score(scores: Dict) -> float:
    """Calculate Stage 2 Tactical Score (Entry Timing)."""
    total = sum(
        scores.get(component, {}).get("score", 50) * weight
        for component, weight in TACTICAL_WEIGHTS.items()
    )
    return round(total, 1)


def get_strategic_classification(score: float) -> Tuple[str, str]:
    """Get classification and action from strategic score."""
    for threshold, classification, action in STRATEGIC_THRESHOLDS:
        if score >= threshold:
            return classification, action
    return "Avoid", "AVOID"


def determine_entry_strategy(strategic_score: float, tactical_score: float) -> str:
    """Determine entry strategy based on both scores."""
    if strategic_score < 50:
        return "IGNORE: Fundamental thesis too weak regardless of technicals"

    if strategic_score >= 80:
        if tactical_score >= 70:
            return "MOMENTUM ENTRY: High conviction + strong technicals = Full position"
        elif tactical_score < 40:
            return "AGGRESSIVE ACCUMULATION: Great company, bad price = DCA opportunity"
        else:
            return "STANDARD ENTRY: Good company, reasonable technicals = Start position"
    elif strategic_score >= 65:
        if tactical_score >= 70:
            return "MOMENTUM ENTRY: Good conviction + breakout = Standard position"
        elif tactical_score < 50:
            return "DCA / LIMIT ORDERS: Good company, poor technicals = Scale in slowly"
        else:
            return "STANDARD ENTRY: Reasonable setup = Standard position"
    else:  # 50-64
        if tactical_score >= 80:
            return "MOMENTUM PLAY: Lower conviction but A+ technicals = Small position"
        else:
            return "WAIT: Below conviction threshold, need better setup or thesis"


def check_missing_analytics(ticker: str) -> List[str]:
    """Check which required analytics files are missing."""
    missing = []
    folder = PROJECT_ROOT / "analytics" / ticker.upper()
    for file_type in REQUIRED_ANALYTICS:
        file_exists = False
        for filename_template in ANALYTICS_FILES[file_type]:
            filename = filename_template.format(ticker=ticker.upper())
            file_path = folder / filename
            if file_path.exists():
                file_exists = True
                break
        if not file_exists:
            missing.append(file_type)
    return missing


def ensure_analytics_exist(ticker: str) -> bool:
    """Ensure all required analytics files exist."""
    missing = check_missing_analytics(ticker)
    if not missing:
        return True

    # Try to generate technical signals (auto-generatable without LLM)
    if "technical" in missing:
        script = PROJECT_ROOT / ".claude" / "skills" / "analytics_generator" / "scripts" / "aggregate_signals.py"
        try:
            result = subprocess.run(
                [sys.executable, str(script), "--ticker", ticker],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print(f"  Warning: Failed to generate technical signals: {result.stderr[:200]}", flush=True)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Re-check what's still missing
    still_missing = check_missing_analytics(ticker)
    if still_missing:
        print(f"__NEEDS_ANALYZE__:{ticker}", file=sys.stderr)
        print(f"Missing files: {', '.join(still_missing)}", file=sys.stderr)
        return False

    return True


def score_stock(ticker: str, name: str = "N/A", auto_analyze: bool = True) -> Optional[StockScore]:
    """Score a single stock using Two-Stage system."""
    print(f"Scoring {ticker}...", flush=True)

    # Ensure all required analytics files exist
    if not ensure_analytics_exist(ticker):
        return None

    # Gather context from analytics files
    context = {
        "thesis": get_analytics_file(ticker, "thesis"),
        "fundamental": get_analytics_file(ticker, "fundamental"),
        "technical_analysis": get_analytics_file(ticker, "technical"),
    }

    # Get price data from watchlist
    price_data = get_price_data(ticker)
    if price_data:
        context.update(price_data)

    # Build prompt and score
    prompt = build_scoring_prompt(ticker, name, context)
    scores = call_claude_for_scoring(prompt)

    if not scores:
        print(f"  Error: LLM scoring failed for {ticker}", flush=True)
        return None

    # Calculate Stage 1: Strategic Score
    strategic_score = calculate_strategic_score(scores)

    # Calculate Stage 2: Tactical Score
    tactical_score = calculate_tactical_score(scores)

    # Get classification from strategic score
    classification, base_action = get_strategic_classification(strategic_score)

    # Determine entry strategy combining both stages
    entry_strategy = determine_entry_strategy(strategic_score, tactical_score)

    # Extract fair value
    fair_value_data = scores.pop("fair_value", {})
    fair_value = fair_value_data.get("price") if isinstance(fair_value_data, dict) else None
    fair_value_method = fair_value_data.get("method") if isinstance(fair_value_data, dict) else None
    fair_value_confidence = fair_value_data.get("confidence") if isinstance(fair_value_data, dict) else None

    # Extract thesis status
    thesis_status = scores.pop("thesis_status", "INTACT")

    # Convert to ScoreComponent objects
    components = {}
    for k, v in scores.items():
        if isinstance(v, dict) and "score" in v:
            components[k] = ScoreComponent(
                score=v.get("score", 50),
                reasoning=v.get("reasoning", ""),
                evidence=v.get("evidence", [])
            )

    return StockScore(
        ticker=ticker.upper(),
        name=name,
        strategic_score=strategic_score,
        tactical_score=tactical_score,
        classification=classification,
        recommended_action=base_action,
        entry_strategy=entry_strategy,
        components=components,
        calculated_at=datetime.now().isoformat(),
        fair_value=fair_value,
        fair_value_method=fair_value_method,
        fair_value_confidence=fair_value_confidence,
        thesis_status=thesis_status
    )


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


def format_console_output(results: list) -> None:
    """Print results in mobile-friendly table format."""
    print(f"\n{'Ticker':<8} {'Strat':<8} {'Tact':<8} {'Thesis':<8} {'Fund':<8} {'Upside':<8} {'Action':<10}")
    print("-" * 90)

    for r in results:
        comps = r.get('components', {})
        thesis = comps.get('thesis', {}).get('score', 50)
        fund = comps.get('fundamental', {}).get('score', 50)
        upside = comps.get('upside', {}).get('score', 50)
        action = r.get('recommended_action', 'N/A')

        strat = r['strategic_score']
        tact = r['tactical_score']
        entry = r.get('entry_strategy', '')[:50]

        print(f"{r['ticker']:<8} {strat:<8.1f} {tact:<8.1f} {thesis:<8} {fund:<8} {upside:<8} {action:<10}")
        print(f"         Entry: {entry}")

        if r.get('fair_value'):
            print(f"         Fair Value: ${r['fair_value']} | Confidence: {r.get('fair_value_confidence', 'N/A')}")


def stock_score_to_dict(score: StockScore) -> Dict:
    """Convert StockScore dataclass to dict for JSON serialization."""
    return {
        "ticker": score.ticker,
        "name": score.name,
        "strategic_score": score.strategic_score,
        "tactical_score": score.tactical_score,
        "classification": score.classification,
        "recommended_action": score.recommended_action,
        "entry_strategy": score.entry_strategy,
        "components": {
            k: {"score": v.score, "reasoning": v.reasoning, "evidence": v.evidence}
            for k, v in (score.components or {}).items()
        },
        "calculated_at": score.calculated_at,
        "fair_value": score.fair_value,
        "fair_value_method": score.fair_value_method,
        "fair_value_confidence": score.fair_value_confidence,
        "thesis_status": score.thesis_status,
    }


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Two-Stage Stock Scoring: Strategic (What) + Tactical (When)"
    )
    parser.add_argument("--ticker", help="Single ticker to score")
    parser.add_argument("--tickers", help="Comma-separated tickers")
    parser.add_argument("--all", action="store_true", help="Score all watchlist stocks")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--min-score", type=float, default=0, help="Minimum strategic score to display")

    args = parser.parse_args()

    # Load watchlist for ticker names
    watchlist = load_watchlist()

    # Get tickers to process
    if args.all:
        tickers = list(watchlist.keys())
    elif args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    elif args.ticker:
        tickers = [args.ticker.upper()]
    else:
        parser.error("Must specify --ticker, --tickers, or --all")

    # Score each stock
    results = []
    failed = []
    for ticker in tickers:
        entry = watchlist.get(ticker.upper(), {})
        name = entry.get("name", "N/A")
        result = score_stock(ticker, name)

        if result:
            result_dict = stock_score_to_dict(result)
            if result_dict["strategic_score"] >= args.min_score:
                results.append(result_dict)
        else:
            failed.append(ticker)

    if failed:
        print(f"\nFailed to score: {', '.join(failed)}", flush=True)

    # Sort by strategic score descending
    results.sort(key=lambda x: x["strategic_score"], reverse=True)

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
