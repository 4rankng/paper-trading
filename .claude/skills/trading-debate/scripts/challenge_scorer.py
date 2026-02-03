#!/usr/bin/env python3
"""
Challenge Scorer - Evaluates challenge quality and determines success/failure.

Challenge Quality Criteria:
- Target persona concedes → 100% success
- Target persona justifies with weak evidence → 50% success
- Target persona justifies with strong evidence → 0% success
- Challenge ignored/irrelevant → -100% (penalty)

Used by the debate orchestrator to score challenges in real-time.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ChallengeOutcome(Enum):
    """Possible outcomes of a challenge."""
    CONCEDED = "conceded"
    WEAKLY_DEFENDED = "weakly_defended"
    STRONGLY_DEFENDED = "strongly_defended"
    IRRELEVANT = "irrelevant"


@dataclass
class Challenge:
    """A challenge from one persona to another."""
    challenger: str
    target: str
    round_number: int
    challenge_text: str
    response_text: str = ""
    outcome: Optional[ChallengeOutcome] = None
    quality_score: float = 0.5


@dataclass
class ChallengeResult:
    """Result of a scored challenge."""
    success: bool
    quality_score: float
    outcome: ChallengeOutcome
    reason: str


class ChallengeScorer:
    """
    Evaluates challenge quality and determines success.

    The scoring system incentivizes:
    - Specific, evidence-based challenges
    - Attacks on weak reasoning
    - Identification of logical flaws

    And penalizes:
    - Generic challenges
    - Challenges already addressed
    - Challenges without supporting evidence
    """

    # Quality indicators for strong defenses
    STRONG_DEFENSE_PHRASES = [
        "data shows",
        "analytics indicate",
        "technical analysis confirms",
        "fundamental support",
        "volume validates",
        "statistically significant",
        "historical pattern",
        "evidence suggests",
        "price action confirms",
        "metrics support"
    ]

    # Quality indicators for weak defenses
    WEAK_DEFENSE_PHRASES = [
        "i think",
        "feels like",
        "probably",
        "maybe",
        "should be",
        "hopefully",
        "gut feeling",
        "intuition",
        "typically",
        "usually"
    ]

    # Indicators of concessions
    CONCESSION_PHRASES = [
        "good point",
        "you're right",
        "i concede",
        "i stand corrected",
        "valid concern",
        "acknowledged",
        "fair point",
        "agreed",
        "that's a fair critique",
        "i withdraw that"
    ]

    def __init__(self, verbose: bool = False):
        """Initialize scorer."""
        self.verbose = verbose

    def score_challenge(self, challenge: Challenge) -> ChallengeResult:
        """
        Score a challenge based on the response.

        Returns ChallengeResult with success, quality_score, outcome, and reason.
        """
        response_lower = challenge.response_text.lower()
        challenge_lower = challenge.challenge_text.lower()

        # Check for concession
        if self._is_concession(response_lower):
            return ChallengeResult(
                success=True,
                quality_score=1.0,
                outcome=ChallengeOutcome.CONCEDED,
                reason="Target persona conceded the point"
            )

        # Check for irrelevant challenge
        if self._is_irrelevant(challenge, response_lower):
            return ChallengeResult(
                success=False,
                quality_score=-1.0,
                outcome=ChallengeOutcome.IRRELEVANT,
                reason="Challenge was ignored or deemed irrelevant"
            )

        # Check defense strength
        if self._has_strong_defense(response_lower):
            return ChallengeResult(
                success=False,
                quality_score=0.0,
                outcome=ChallengeOutcome.STRONGLY_DEFENDED,
                reason="Target provided strong evidence-based defense"
            )

        if self._has_weak_defense(response_lower):
            return ChallengeResult(
                success=True,
                quality_score=0.5,
                outcome=ChallengeOutcome.WEAKLY_DEFENDED,
                reason="Target provided weak defense"
            )

        # Default: partial success (inconclusive)
        return ChallengeResult(
            success=False,
            quality_score=0.25,
            outcome=ChallengeOutcome.STRONGLY_DEFENDED,
            reason="Defense was adequate"
        )

    def _is_concession(self, response: str) -> bool:
        """Check if response contains concession indicators."""
        for phrase in self.CONCESSION_PHRASES:
            if phrase in response:
                return True
        return False

    def _has_strong_defense(self, response: str) -> bool:
        """Check if response contains strong evidence indicators."""
        count = sum(1 for phrase in self.STRONG_DEFENSE_PHRASES if phrase in response)
        return count >= 2  # At least 2 strong indicators

    def _has_weak_defense(self, response: str) -> bool:
        """Check if response relies on weak reasoning."""
        weak_count = sum(1 for phrase in self.WEAK_DEFENSE_PHRASES if phrase in response)
        strong_count = sum(1 for phrase in self.STRONG_DEFENSE_PHRASES if phrase in response)
        return weak_count >= 2 and strong_count == 0

    def _is_irrelevant(self, challenge: Challenge, response: str) -> bool:
        """Check if challenge was ignored or deemed irrelevant."""
        # Very short response might indicate ignoring
        if len(challenge.response_text.strip()) < 50:
            return True

        # Response doesn't address the challenge topic
        challenge_words = set(challenge.challenge_text.lower().split())
        response_words = set(response.split())

        # If less than 20% word overlap, might be irrelevant
        overlap = len(challenge_words & response_words) / max(len(challenge_words), 1)
        if overlap < 0.2:
            return True

        return False

    def score_batch(self, challenges: List[Challenge]) -> Dict[str, ChallengeResult]:
        """Score multiple challenges at once."""
        return {c.challenger: self.score_challenge(c) for c in challenges}

    def get_challenge_success_rate(self, results: Dict[str, ChallengeResult]) -> float:
        """Calculate success rate from challenge results."""
        if not results:
            return 0.5

        successful = sum(1 for r in results.values() if r.success)
        return successful / len(results)

    def should_mute_persona(self, persona: str, results: Dict[str, ChallengeResult],
                           min_challenges: int = 3, mute_threshold: float = 0.30) -> bool:
        """Determine if a persona should be muted based on challenge results."""
        persona_results = [r for k, r in results.items() if k == persona]

        if len(persona_results) < min_challenges:
            return False

        success_rate = sum(1 for r in persona_results if r.success) / len(persona_results)
        return success_rate < mute_threshold


def analyze_debate_transcript(transcript: str, personas: List[str]) -> Dict:
    """
    Analyze a debate transcript and extract challenge outcomes.

    This is a helper for post-debate analysis when LLM has completed the debate.
    The LLM should structure its debate output to facilitate parsing.

    Expected format in transcript:
    ### Round N Challenges
    **[Persona] challenges [Persona]:**
    [Challenge text]

    **[Persona] responds:**
    [Response text]
    """
    scorer = ChallengeScorer()

    # This would parse the transcript and score challenges
    # For now, return empty structure
    return {
        "rounds": [],
        "challenges": [],
        "outcomes": {}
    }


def main():
    """CLI for testing challenge scorer."""
    import argparse

    parser = argparse.ArgumentParser(description="Score debate challenges")
    parser.add_argument("--test", action="store_true", help="Run test examples")
    parser.add_argument("--challenge", help="Challenge text")
    parser.add_argument("--response", help="Response text")
    parser.add_argument("--challenger", default="TestPersona")
    parser.add_argument("--target", default="TestTarget")

    args = parser.parse_args()
    scorer = ChallengeScorer(verbose=True)

    if args.test:
        print("=== Challenge Scorer Tests ===\n")

        # Test 1: Concession
        c1 = Challenge(
            challenger="Short-Seller",
            target="Trend Architect",
            round_number=1,
            challenge_text="The EMA stack is weakening, RSI diverging.",
            response_text="You're right, I concede that the divergence is concerning."
        )
        result1 = scorer.score_challenge(c1)
        print(f"Test 1 (Concession): {result1.outcome.value}, score={result1.quality_score}")

        # Test 2: Strong defense
        c2 = Challenge(
            challenger="Short-Seller",
            target="Trend Architect",
            round_number=1,
            challenge_text="The trend is broken.",
            response_text="Data shows EMA 20 > EMA 50 > EMA 200. Price action confirms upward momentum. Volume validates the move."
        )
        result2 = scorer.score_challenge(c2)
        print(f"Test 2 (Strong Defense): {result2.outcome.value}, score={result2.quality_score}")

        # Test 3: Weak defense
        c3 = Challenge(
            challenger="Short-Seller",
            target="Trend Architect",
            round_number=1,
            challenge_text="The trend looks weak.",
            response_text="I think it should be fine. Probably just a small pullback. Usually these recover."
        )
        result3 = scorer.score_challenge(c3)
        print(f"Test 3 (Weak Defense): {result3.outcome.value}, score={result3.quality_score}")

    elif args.challenge and args.response:
        challenge = Challenge(
            challenger=args.challenger,
            target=args.target,
            round_number=1,
            challenge_text=args.challenge,
            response_text=args.response
        )
        result = scorer.score_challenge(challenge)
        print(f"\n=== Challenge Result ===")
        print(f"Outcome: {result.outcome.value}")
        print(f"Success: {result.success}")
        print(f"Quality Score: {result.quality_score}")
        print(f"Reason: {result.reason}")


if __name__ == "__main__":
    main()
