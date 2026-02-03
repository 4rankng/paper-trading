#!/usr/bin/env python3
"""
Risk-Adjusted Buy Score Calculator

Applies qualitative risk adjustments to quantitative buy scores to prevent
overly optimistic scoring of high-risk speculative stocks.

This solves the problem where a stock like MATH gets 99/100 based on
fundamentals (P/E, ROE, margins) but has severe qualitative risks:
- Crypto winter exposure
- Chinese VIE structure
- Micro-cap illiquidity
- Unproven earnings sustainability

NOTE: Technical health penalties are DISABLED. Technical health is used for
TIMING decisions (via llm_scorer.py timing override) and does NOT reduce
the buy_score. A stock with great fundamentals but poor technicals should
have a high buy_score with a WAIT recommendation.
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


@dataclass
class RiskAdjustment:
    """Single risk adjustment with reasoning."""
    penalty: int  # Points to subtract from buy score
    reason: str
    category: str


@dataclass
class RiskProfile:
    """Complete risk assessment for a stock."""
    base_score: float
    adjusted_score: float
    total_penalty: int
    adjustments: List[RiskAdjustment]
    classification: str
    recommended_action: str


class RiskDetector:
    """Detects high-risk patterns from analytics files."""

    # High-risk phenomenon types that trigger automatic penalties
    HIGH_RISK_PHENOMENA = {
        "turnaround_speculative": 25,
        "turnaround": 15,
        "speculative": 20,
        "bankruptcy_risk": 40,
        "distressed": 30,
    }

    # Risk keywords in thesis that trigger penalties
    # Grouped to avoid duplicate penalties for similar concepts
    RISK_KEYWORD_GROUPS = {
        "vie": ["chinese vie", "vie structure", "variable interest entity"],
        "governance": ["governance risk"],
        "crypto": ["crypto winter", "crypto exposure", "100% crypto", "crypto-dependent"],
        "concentration": ["sector concentration", "customer concentration"],
        "regulatory": ["regulatory uncertainty", "regulatory risk"],
        "accounting": ["accounting risk", "accounting quality"],
        "distress": ["going concern", "bankruptcy risk", "financial distress"],
        "delisting": ["delisting risk", "delisting", "nasdaq compliance"],
        "sustainability": ["one-time gain", "unproven sustainability", "earnings quality"],
        "binary": ["binary outcome", "all or nothing", "lottery ticket"],
    }

    # Base penalty for each risk group
    RISK_GROUP_PENALTIES = {
        "vie": 15,
        "governance": 10,
        "crypto": 15,
        "concentration": 10,
        "regulatory": 10,
        "accounting": 15,
        "distress": 30,
        "delisting": 20,
        "sustainability": 10,
        "binary": 20,
    }

    # Technical health score penalties - DISABLED
    # Technical health is now used for timing decisions only (see llm_scorer.py)
    # Tech penalties are NOT applied to buy_score
    TECH_HEALTH_PENALTIES = []  # Disabled - technicals affect timing, not score

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.analytics_dir = PROJECT_ROOT / "analytics" / self.ticker

    def detect_phenomenon_type(self) -> Tuple[str, Optional[int]]:
        """Detect phenomenon type from thesis file.

        Returns:
            (phenomenon_type, penalty) tuple
        """
        thesis_file = self.analytics_dir / f"{self.ticker}_investment_thesis.md"
        if not thesis_file.exists():
            return "unknown", None

        content = thesis_file.read_text().lower()

        # Look for phenomenon classification
        for pattern, penalty in self.HIGH_RISK_PHENOMENA.items():
            if pattern in content:
                return pattern, penalty

        # Check for "Phenomenon:" or similar headings
        match = re.search(r'(?:phenomenon|classification)[:\s]*([^\n]+)', content)
        if match:
            phenomenon = match.group(1).strip().lower()
            for pattern, penalty in self.HIGH_RISK_PHENOMENA.items():
                if pattern in phenomenon:
                    return pattern, penalty

        return "unknown", None

    def detect_risk_keywords(self) -> List[RiskAdjustment]:
        """Detect risk keywords in thesis file using grouped detection."""
        adjustments = []
        thesis_file = self.analytics_dir / f"{self.ticker}_investment_thesis.md"

        if not thesis_file.exists():
            return adjustments

        content = thesis_file.read_text().lower()

        # Check each risk group
        for group_name, keywords in self.RISK_KEYWORD_GROUPS.items():
            # Check if any keyword in this group is found
            found_keyword = None
            for keyword in keywords:
                if keyword in content:
                    found_keyword = keyword
                    break

            if found_keyword:
                penalty = self.RISK_GROUP_PENALTIES.get(group_name, 10)
                # Check if this group is already added
                existing = any(group_name in adj.reason.lower() for adj in adjustments)
                if not existing:
                    adjustments.append(RiskAdjustment(
                        penalty=penalty,
                        reason=f"Risk factor: {group_name.title()} ({found_keyword})",
                        category="qualitative"
                    ))

        return adjustments

    def get_technical_health_score(self) -> Optional[float]:
        """Extract technical health score from technical analysis file."""
        # Try technical_analysis.md (now contains the signal dashboard)
        tech_file = self.analytics_dir / f"{self.ticker}_technical_analysis.md"
        if tech_file.exists():
            content = tech_file.read_text()
            # Look for "Overall Technical Health Score" or "Health Score: XX.X/100"
            match = re.search(r'Overall Technical Health Score[^\d]+(\d+\.?\d*)', content)
            if not match:
                match = re.search(r'Health Score[^\d]+(\d+\.?\d*)', content)
            if match:
                return float(match.group(1))

        return None

    def calculate_technical_penalty(self) -> Optional[RiskAdjustment]:
        """Calculate penalty based on technical health score.

        DISABLED: Technical health is used for timing decisions only.
        See llm_scorer.py apply_timing_override() for how technicals
        affect recommended_action WITHOUT reducing buy_score.
        """
        return None  # Disabled - technicals affect timing, not score

    def get_market_cap(self) -> Optional[float]:
        """Get market cap from fundamental analysis."""
        fundamental_file = self.analytics_dir / f"{self.ticker}_fundamental_analysis.md"
        if not fundamental_file.exists():
            return None

        content = fundamental_file.read_text()
        match = re.search(r'Market Cap[^$]*\$?([\d.]+)[MB]?', content, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # Check if it's in millions or billions
            if 'billion' in content[match.start():match.start()+50].lower():
                return value * 1e9
            elif 'million' in content[match.start():match.start()+50].lower():
                return value * 1e6
        return None

    def calculate_microcap_penalty(self) -> Optional[RiskAdjustment]:
        """Note: Micro-cap/nano-cap status is NOT automatically penalized.

        The LLM scorer evaluates holistically:
        - A nano-cap with 75% GM, 53% margins, zero debt = legitimate opportunity
        - A nano-cap with poor fundamentals = speculative lottery ticket

        Let the LLM decide based on FULL context, not hardcoded size penalties.
        """
        return None

    def check_missing_analytics(self) -> bool:
        """Check if required analytics files exist."""
        return self.analytics_dir.exists()


def calculate_risk_adjusted_score(
    ticker: str,
    base_score: float,
    fundamental_score: Optional[float] = None,
    technical_score: Optional[float] = None
) -> RiskProfile:
    """Calculate risk-adjusted buy score.

    Args:
        ticker: Stock ticker symbol
        base_score: Original calculated buy score (0-100)
        fundamental_score: Optional fundamental component score
        technical_score: Optional technical component score

    Returns:
        RiskProfile with adjusted score and breakdown of adjustments
    """
    detector = RiskDetector(ticker)

    # Check if analytics exist
    if not detector.check_missing_analytics():
        # No analytics available, return base score with warning
        return RiskProfile(
            base_score=base_score,
            adjusted_score=base_score,
            total_penalty=0,
            adjustments=[],
            classification=get_classification(base_score)[0],
            recommended_action=get_classification(base_score)[1]
        )

    adjustments = []

    # 1. Check phenomenon type
    phenomenon, penalty = detector.detect_phenomenon_type()
    if penalty:
        adjustments.append(RiskAdjustment(
            penalty=penalty,
            reason=f"High-risk phenomenon: {phenomenon.replace('_', ' ').title()}",
            category="phenomenon"
        ))

    # 2. Technical health penalty
    tech_penalty = detector.calculate_technical_penalty()
    if tech_penalty:
        adjustments.append(tech_penalty)

    # 3. Risk keyword detection
    keyword_adjustments = detector.detect_risk_keywords()
    adjustments.extend(keyword_adjustments)

    # 4. (DISABLED) Divergence penalty for high base score + poor technicals
    # Technicals now affect timing/recommendation, not buy_score
    # The timing override in llm_scorer.py handles this by downgrading action to WATCH

    # Calculate total penalty (cap at 50 points to avoid overselling)
    total_penalty = min(50, sum(adj.penalty for adj in adjustments))

    # Apply penalty
    adjusted_score = max(10, base_score - total_penalty)  # Floor at 10

    # Get classification
    classification, action = get_classification(adjusted_score)

    return RiskProfile(
        base_score=base_score,
        adjusted_score=round(adjusted_score, 1),
        total_penalty=total_penalty,
        adjustments=adjustments,
        classification=classification,
        recommended_action=action
    )


def get_classification(score: float) -> Tuple[str, str]:
    """Get classification and action from buy score.

    Returns:
        (classification, action) tuple
    """
    if score >= 75:
        return "Strong Buy", "BUY"
    elif score >= 60:
        return "Buy", "BUY"
    elif score >= 50:
        return "Moderate Buy", "WATCH"
    elif score >= 40:
        return "Speculative Buy", "WATCH"
    else:
        return "Avoid", "AVOID"


def format_profile(profile: RiskProfile) -> str:
    """Format risk profile for console output."""
    lines = [
        f"Base Score: {profile.base_score}",
        f"Adjusted Score: {profile.adjusted_score}",
        f"Total Penalty: -{profile.total_penalty} points",
        "",
        "Adjustments:"
    ]
    for adj in profile.adjustments:
        lines.append(f"  -{adj.penalty} {adj.reason} [{adj.category}]")

    lines.extend([
        "",
        f"Classification: {profile.classification}",
        f"Action: {profile.recommended_action}"
    ])
    return "\n".join(lines)


def main():
    """CLI for risk-adjusted scoring."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate risk-adjusted buy scores"
    )
    parser.add_argument("--ticker", required=True, help="Stock ticker")
    parser.add_argument("--base-score", type=float, required=True,
                       help="Original calculated buy score")
    parser.add_argument("--fundamental", type=float, help="Fundamental score")
    parser.add_argument("--technical", type=float, help="Technical score")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    profile = calculate_risk_adjusted_score(
        args.ticker,
        args.base_score,
        args.fundamental,
        args.technical
    )

    if args.json:
        output = {
            "ticker": args.ticker.upper(),
            "base_score": profile.base_score,
            "adjusted_score": profile.adjusted_score,
            "total_penalty": profile.total_penalty,
            "adjustments": [
                {
                    "penalty": adj.penalty,
                    "reason": adj.reason,
                    "category": adj.category
                }
                for adj in profile.adjustments
            ],
            "classification": profile.classification,
            "recommended_action": profile.recommended_action
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Risk-Adjusted Buy Score: {args.ticker.upper()}")
        print('='*60)
        print(format_profile(profile))


if __name__ == "__main__":
    main()
