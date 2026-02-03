#!/usr/bin/env python3
"""
Bayesian Updater - Tracks confidence convergence during debates.

Uses Bayesian updating to track:
- P(Buy) vs P(Sell) probability distribution
- Confidence interval width
- Convergence detection for early stopping

Math:
- Prior: uniform (0.5, 0.5)
- After each round: update based on weighted persona votes
- Confidence = |P(Buy) - 0.5| × 2
- Stop when confidence > threshold AND min rounds met
"""
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class Verdict(Enum):
    """Possible verdict values."""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WATCH = "WATCH"
    AVOID = "AVOID"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class BeliefState:
    """Current probability distribution over verdicts."""
    p_buy: float = 0.5
    p_sell: float = 0.5
    confidence: float = 0.0
    round_number: int = 1

    def to_dict(self) -> Dict:
        return {
            "round": self.round_number,
            "p_buy": self.p_buy,
            "p_sell": self.p_sell,
            "confidence": self.confidence
        }


@dataclass
class ConvergenceResult:
    """Result of convergence check."""
    converged: bool
    confidence: float
    verdict: str
    reason: str


class BayesianUpdater:
    """
    Tracks Bayesian belief updates during debate.

    The confidence metric represents how "sure" the group is:
    - 0.0 = complete uncertainty (50/50)
    - 1.0 = complete certainty (unanimous agreement)
    """

    def __init__(self, confidence_threshold: float = 0.90):
        """
        Initialize Bayesian updater.

        Args:
            confidence_threshold: Stop when confidence exceeds this (default 0.90)
        """
        self.confidence_threshold = confidence_threshold
        self.history: List[BeliefState] = []
        self.current_belief = BeliefState()

    def update(self, votes: Dict[str, str], weights: Dict[str, float]) -> BeliefState:
        """
        Update belief state based on weighted votes.

        Args:
            votes: Map of persona -> verdict (BUY/SELL/WATCH/AVOID)
            weights: Map of persona -> weight (0-1)

        Returns:
            Updated BeliefState
        """
        # Convert verdicts to buy/sell preference
        buy_preference = self._verdicts_to_preferences(votes)

        # Calculate weighted preference
        total_weight = 0.0
        weighted_buy = 0.0

        for persona, preference in buy_preference.items():
            weight = weights.get(persona, 0.5)
            total_weight += weight
            weighted_buy += preference * weight

        # Normalize
        if total_weight > 0:
            p_buy = weighted_buy / total_weight
        else:
            p_buy = 0.5

        p_sell = 1 - p_buy

        # Calculate confidence (distance from uncertainty)
        confidence = abs(p_buy - 0.5) * 2

        # Update current belief
        self.current_belief = BeliefState(
            p_buy=p_buy,
            p_sell=p_sell,
            confidence=confidence,
            round_number=self.current_belief.round_number + 1
        )

        self.history.append(self.current_belief)
        return self.current_belief

    def _verdicts_to_preferences(self, votes: Dict[str, str]) -> Dict[str, float]:
        """
        Convert verdict strings to buy/sell preference scores.

        Returns:
            Dict mapping persona -> preference (-1.0 to 1.0)
        """
        preference = {}

        for persona, verdict in votes.items():
            v = verdict.upper().replace(" ", "_")

            if v in ["STRONG_BUY", "BUY"]:
                preference[persona] = 1.0
            elif v in ["STRONG_SELL", "SELL", "AVOID"]:
                preference[persona] = -1.0
            elif v == "WATCH":
                preference[persona] = 0.0
            elif v == "HOLD":
                preference[persona] = 0.0
            else:
                # Default to weak buy/neutral
                preference[persona] = 0.25

        return preference

    def check_convergence(self, min_rounds: int = 3) -> ConvergenceResult:
        """
        Check if debate has converged.

        Args:
            min_rounds: Minimum rounds before convergence can be declared

        Returns:
            ConvergenceResult with converged bool and details
        """
        if self.current_belief.round_number < min_rounds:
            return ConvergenceResult(
                converged=False,
                confidence=self.current_belief.confidence,
                verdict=self._get_current_verdict(),
                reason=f"Minimum rounds not met ({self.current_belief.round_number}/{min_rounds})"
            )

        if self.current_belief.confidence >= self.confidence_threshold:
            return ConvergenceResult(
                converged=True,
                confidence=self.current_belief.confidence,
                verdict=self._get_current_verdict(),
                reason=f"Confidence threshold reached ({self.current_belief.confidence:.2%} >= {self.confidence_threshold:.2%})"
            )

        # Check for stagnation (no significant change in last 2 rounds)
        if len(self.history) >= 3:
            recent_change = abs(self.history[-1].confidence - self.history[-2].confidence)
            if recent_change < 0.05:  # Less than 5% change
                return ConvergenceResult(
                    converged=True,
                    confidence=self.current_belief.confidence,
                    verdict=self._get_current_verdict(),
                    reason="Confidence stabilized (no significant change in recent rounds)"
                )

        return ConvergenceResult(
            converged=False,
            confidence=self.current_belief.confidence,
            verdict=self._get_current_verdict(),
            reason=f"Confidence below threshold ({self.current_belief.confidence:.2%} < {self.confidence_threshold:.2%})"
        )

    def _get_current_verdict(self) -> str:
        """Get current verdict based on belief state."""
        p = self.current_belief.p_buy

        if p >= 0.85:
            return "STRONG_BUY"
        elif p >= 0.65:
            return "BUY"
        elif p >= 0.55:
            return "WATCH"
        elif p >= 0.45:
            return "WATCH"  # Neutral zone
        elif p >= 0.35:
            return "AVOID"
        else:
            return "STRONG_SELL"

    def get_confidence_table(self) -> str:
        """Generate markdown table of confidence history."""
        if not self.history:
            return "No rounds completed yet."

        lines = ["## Bayesian Confidence Tracker\n"]
        lines.append("| Round | P(Buy) | P(Sell) | Confidence | Change | Verdict |")
        lines.append("|-------|--------|---------|------------|--------|---------|")

        prev_conf = 0.0
        for state in self.history:
            change = state.confidence - prev_conf
            change_str = f"+{change:.2%}" if change >= 0 else f"{change:.2%}"

            verdict = self._verdict_from_prob(state.p_buy)

            lines.append(f"| {state.round_number} | {state.p_buy:.2%} | "
                        f"{state.p_sell:.2%} | {state.confidence:.2%} | "
                        f"{change_str} | {verdict} |")

            prev_conf = state.confidence

        # Add convergence status
        conv = self.check_convergence()
        lines.append(f"\n**Status:** {'✓ Converged' if conv.converged else '○ Ongoing'}")
        lines.append(f"**Reason:** {conv.reason}")

        return "\n".join(lines)

    def _verdict_from_prob(self, p_buy: float) -> str:
        """Convert buy probability to verdict string."""
        if p_buy >= 0.85:
            return "STRONG_BUY"
        elif p_buy >= 0.65:
            return "BUY"
        elif p_buy >= 0.45:
            return "WATCH"
        elif p_buy >= 0.35:
            return "AVOID"
        else:
            return "STRONG_SELL"

    def reset(self):
        """Reset for a new debate."""
        self.history = []
        self.current_belief = BeliefState()

    def get_summary(self) -> Dict:
        """Get summary of current state."""
        return {
            "current_belief": self.current_belief.to_dict(),
            "rounds_completed": len(self.history),
            "converged": self.check_convergence().converged,
            "verdict": self._get_current_verdict()
        }


def simulate_debate() -> None:
    """Simulate a debate to demonstrate Bayesian updating."""
    print("=== Bayesian Updating Simulation ===\n")

    updater = BayesianUpdater(confidence_threshold=0.90)

    # Simulate personas and their weights
    personas = [
        "Trend Architect",
        "Tape Reader",
        "Risk Manager",
        "Short-Seller",
        "Macro Strategist"
    ]

    # Equal weights for simulation
    weights = {p: 1.0 for p in personas}

    # Round 1: Mixed votes
    print("Round 1: Mixed initial votes")
    votes1 = {
        "Trend Architect": "BUY",
        "Tape Reader": "BUY",
        "Risk Manager": "WATCH",
        "Short-Seller": "AVOID",
        "Macro Strategist": "WATCH"
    }
    state1 = updater.update(votes1, weights)
    print(f"  P(Buy)={state1.p_buy:.2%}, Confidence={state1.confidence:.2%}\n")

    # Round 2: Convergence toward buy
    print("Round 2: Convergence toward BUY")
    votes2 = {
        "Trend Architect": "BUY",
        "Tape Reader": "BUY",
        "Risk Manager": "BUY",
        "Short-Seller": "WATCH",
        "Macro Strategist": "BUY"
    }
    state2 = updater.update(votes2, weights)
    print(f"  P(Buy)={state2.p_buy:.2%}, Confidence={state2.confidence:.2%}\n")

    # Round 3: Strong convergence
    print("Round 3: Strong convergence")
    votes3 = {
        "Trend Architect": "BUY",
        "Tape Reader": "BUY",
        "Risk Manager": "BUY",
        "Short-Seller": "BUY",
        "Macro Strategist": "BUY"
    }
    state3 = updater.update(votes3, weights)
    print(f"  P(Buy)={state3.p_buy:.2%}, Confidence={state3.confidence:.2%}\n")

    # Check convergence
    conv = updater.check_convergence(min_rounds=3)
    print(f"Convergence: {conv.converged}")
    print(f"Verdict: {conv.verdict}")
    print(f"Reason: {conv.reason}\n")

    print(updater.get_confidence_table())


def main():
    """CLI for Bayesian updater."""
    import argparse

    parser = argparse.ArgumentParser(description="Bayesian confidence tracking")
    parser.add_argument("--simulate", action="store_true", help="Run simulation")
    parser.add_argument("--threshold", type=float, default=0.90,
                       help="Confidence threshold (default 0.90)")
    parser.add_argument("--votes", nargs="+", help="Votes in format PERSONA:VERDICT")

    args = parser.parse_args()

    if args.simulate:
        simulate_debate()

    elif args.votes:
        updater = BayesianUpdater(confidence_threshold=args.threshold)

        # Parse votes
        votes = {}
        weights = {}
        for v in args.votes:
            parts = v.split(":")
            if len(parts) == 2:
                votes[parts[0]] = parts[1]
                weights[parts[0]] = 1.0

        state = updater.update(votes, weights)
        conv = updater.check_convergence()

        print(f"\nP(Buy): {state.p_buy:.2%}")
        print(f"P(Sell): {state.p_sell:.2%}")
        print(f"Confidence: {state.confidence:.2%}")
        print(f"Verdict: {conv.verdict}")
        print(f"Converged: {conv.converged}")


if __name__ == "__main__":
    main()
