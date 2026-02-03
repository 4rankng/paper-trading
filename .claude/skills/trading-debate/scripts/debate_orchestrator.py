#!/usr/bin/env python3
"""
Debate Orchestrator - Manages parallel challenge-response debates.

Implements efficient parallel challenge mode:
- All personas issue challenges simultaneously
- Challenges grouped by target for batched responses
- Reduced from O(n²) to O(n) per round
- Integrates with persona tracker and Bayesian updater
"""
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime

from persona_tracker import PersonaTracker
from challenge_scorer import ChallengeScorer, Challenge, ChallengeResult
from bayesian_updater import BayesianUpdater


@dataclass
class ChallengeBatch:
    """A batch of challenges targeting a specific persona."""
    target_persona: str
    challenges: List[Challenge] = field(default_factory=list)

    def add_challenge(self, challenge: Challenge):
        """Add a challenge to this batch."""
        self.challenges.append(challenge)

    def get_prompt(self) -> str:
        """Generate prompt for this batch."""
        prompt = f"\n## Challenges to {self.target_persona}\n\n"
        for i, c in enumerate(self.challenges, 1):
            prompt += f"**{c.challenger} challenges:** {c.challenge_text}\n\n"
        return prompt


@dataclass
class ParallelRound:
    """A round of parallel debate."""
    round_number: int
    challenges: Dict[str, Challenge] = field(default_factory=dict)
    responses: Dict[str, str] = field(default_factory=dict)
    results: Dict[str, ChallengeResult] = field(default_factory=dict)
    muted_personas: Set[str] = field(default_factory=set)


@dataclass
class OrchestratorConfig:
    """Configuration for debate orchestrator."""
    mute_threshold: float = 0.30
    min_challenges_before_mute: int = 3
    confidence_threshold: float = 0.90
    min_rounds: int = 3
    max_rounds: int = 5


class DebateOrchestrator:
    """
    Orchestrates parallel challenge-response debates.

    Key features:
    - Parallel challenge issuing (O(n) instead of O(n²))
    - Automatic muting of low-performing personas
    - Bayesian confidence tracking for early convergence
    - Historical persona accuracy weighting
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None,
                 tracker: Optional[PersonaTracker] = None):
        """
        Initialize orchestrator.

        Args:
            config: Configuration for behavior
            tracker: PersonaTracker for historical accuracy
        """
        self.config = config or OrchestratorConfig()
        self.tracker = tracker or PersonaTracker()
        self.scorer = ChallengeScorer()
        self.bayesian = BayesianUpdater(confidence_threshold=self.config.confidence_threshold)

        self.debates: Dict[int, List[ParallelRound]] = {}  # debate_id -> rounds
        self.current_debate_id: Optional[int] = None
        self.personas: List[str] = []

    def start_debate(self, ticker: str, timeframe: str, model: str,
                     personas: List[str], mode: str = "parallel") -> int:
        """
        Start a new debate.

        Args:
            ticker: Stock symbol
            timeframe: Trading timeframe (e.g., "2w")
            model: Debate model (scalping/swing/position/investment)
            personas: List of personas participating
            mode: Debate mode (parallel/sequential/fast)

        Returns:
            Debate ID
        """
        self.personas = personas
        self.current_debate_id = self.tracker.register_debate(
            ticker, timeframe, model, mode, personas
        )
        self.debates[self.current_debate_id] = []
        self.bayesian.reset()

        return self.current_debate_id

    def get_round_prompt(self, round_number: int,
                         opening_statements: Dict[str, str]) -> str:
        """
        Generate prompt for a parallel challenge round.

        Args:
            round_number: Current round number
            opening_statements: Persona -> statement from Phase 1

        Returns:
            Prompt for LLM to issue challenges
        """
        prompt = f"""
## Round {round_number}: Parallel Challenge Phase

Each persona must issue exactly **ONE challenge** to another persona.

**Your Challenge Requirements:**
1. Choose ONE persona whose analysis you disagree with most
2. State clearly WHAT you disagree with
3. Provide counter-evidence or reasoning
4. Keep it concise (100 words max)

**Opening Statements to Challenge:**

"""
        for persona, statement in opening_statements.items():
            prompt += f"\n**{persona}:** {statement[:200]}...\n"

        prompt += """

**Your Response Format:**

```
CHALLENGE_TO: [Persona Name]
DISAGREEMENT: [What you disagree with]
COUNTER_EVIDENCE: [Your reasoning]
```

**Important:** Challenge only ONE persona. Make it specific and evidence-based.
"""
        return prompt

    def process_challenges(self, challenges: List[Tuple[str, str, str]],
                          round_number: int) -> ChallengeBatch:
        """
        Process challenges from all personas.

        Args:
            challenges: List of (challenger, target, challenge_text)
            round_number: Current round number

        Returns:
            ChallengeBatch grouped by target
        """
        # Group by target
        batches: Dict[str, ChallengeBatch] = {}

        for challenger, target, text in challenges:
            if target not in batches:
                batches[target] = ChallengeBatch(target_persona=target)

            challenge = Challenge(
                challenger=challenger,
                target=target,
                round_number=round_number,
                challenge_text=text
            )
            batches[target].add_challenge(challenge)

        return batches

    def get_response_prompts(self, batches: Dict[str, ChallengeBatch],
                            muted_personas: Set[str]) -> Dict[str, str]:
        """
        Generate response prompts for each targeted persona.

        Args:
            batches: Challenge batches grouped by target
            muted_personas: Personas to skip (already muted)

        Returns:
            Dict of persona -> response prompt
        """
        prompts = {}

        for target, batch in batches.items():
            if target in muted_personas:
                continue

            prompt = f"""
## Responses to Challenges

You have received {len(batch.challenges)} challenge(s). Respond to each below.

**Keep responses concise (150 words max per response).**

**Format:**
- If you concede: "I concede on [point] because..."
- If you defend: "The evidence shows [your reasoning]..."

{batch.get_prompt()}

**Your Responses:**
"""
            prompts[target] = prompt

        return prompts

    def score_responses(self, batches: Dict[str, ChallengeBatch],
                       responses: Dict[str, str]) -> Tuple[Dict[str, ChallengeResult], Set[str]]:
        """
        Score all responses and determine which personas to mute.

        Args:
            batches: Challenge batches grouped by target
            responses: Persona -> response text

        Returns:
            Tuple of (results_by_challenger, newly_muted_personas)
        """
        all_results: Dict[str, ChallengeResult] = {}
        challenger_counts: Dict[str, List[ChallengeResult]] = {}
        newly_muted: Set[str] = set()

        # Score each challenge
        for target, batch in batches.items():
            response = responses.get(target, "")

            for challenge in batch.challenges:
                challenge.response_text = response
                result = self.scorer.score_challenge(challenge)
                all_results[challenge.challenger] = result

                # Track by challenger for mute calculation
                if challenge.challenger not in challenger_counts:
                    challenger_counts[challenge.challenger] = []
                challenger_counts[challenge.challenger].append(result)

        # Check for muting
        for challenger, results in challenger_counts.items():
            if self.scorer.should_mute_persona(
                challenger,
                {challenger: r for r in results},
                min_challenges=self.config.min_challenges_before_mute,
                mute_threshold=self.config.mute_threshold
            ):
                newly_muted.add(challenger)

        return all_results, newly_muted

    def get_muted_personas(self, debate_id: Optional[int] = None) -> Set[str]:
        """Get all muted personas for a debate."""
        if debate_id is None:
            debate_id = self.current_debate_id

        if debate_id not in self.debates:
            return set()

        muted = set()
        for round_data in self.debates[debate_id]:
            muted.update(round_data.muted_personas)

        return muted

    def update_bayesian(self, votes: Dict[str, str]) -> Dict:
        """
        Update Bayesian belief state with votes.

        Args:
            votes: Persona -> verdict

        Returns:
            Current belief state as dict
        """
        weights = self.tracker.get_all_weights(
            self.personas,
            min_debates=self.config.min_challenges_before_mute
        )

        state = self.bayesian.update(votes, weights)
        return state.to_dict()

    def check_convergence(self) -> Dict:
        """
        Check if debate has converged.

        Returns:
            Dict with converged (bool), verdict, confidence, reason
        """
        result = self.bayesian.check_convergence(min_rounds=self.config.min_rounds)

        return {
            "converged": result.converged,
            "verdict": result.verdict,
            "confidence": result.confidence,
            "reason": result.reason,
            "round": self.bayesian.current_belief.round_number
        }

    def finalize_debate(self, debate_id: Optional[int] = None,
                       verdict: str = "", conviction: str = "",
                       rounds_completed: int = 0, final_confidence: float = 0.0,
                       challenges_issued: int = 0, challenges_successful: int = 0):
        """
        Finalize a debate with results.

        Args:
            debate_id: Debate ID (uses current if None)
            verdict: Final verdict (BUY/SELL/AVOID/WATCH)
            conviction: Conviction level (HIGH/MEDIUM/LOW)
            rounds_completed: Number of rounds completed
            final_confidence: Final Bayesian confidence
            challenges_issued: Total challenges issued
            challenges_successful: Total successful challenges
        """
        if debate_id is None:
            debate_id = self.current_debate_id

        self.tracker.finalize_debate(
            debate_id, verdict, conviction, rounds_completed,
            final_confidence, challenges_issued, challenges_successful
        )

    def get_debate_summary(self, debate_id: Optional[int] = None) -> Dict:
        """Get summary of a debate."""
        if debate_id is None:
            debate_id = self.current_debate_id

        muted = self.get_muted_personas(debate_id)
        conv = self.check_convergence()

        return {
            "debate_id": debate_id,
            "personas": self.personas,
            "muted_personas": list(muted),
            "rounds_completed": len(self.debates.get(debate_id, [])),
            "current_verdict": conv["verdict"],
            "confidence": conv["confidence"],
            "converged": conv["converged"],
            "convergence_reason": conv["reason"]
        }

    def get_status_display(self) -> str:
        """Get current debate status as formatted string."""
        summary = self.get_debate_summary()
        muted = summary["muted_personas"]

        lines = [
            "## Debate Status",
            "",
            f"**Round:** {summary['rounds_completed']}",
            f"**Verdict:** {summary['current_verdict']}",
            f"**Confidence:** {summary['confidence']:.2%}",
            f"**Status:** {'✓ Converged' if summary['converged'] else '○ In Progress'}",
            ""
        ]

        if muted:
            lines.append("**Muted Personas:**")
            for m in muted:
                lines.append(f"  - {m}")
            lines.append("")

        lines.append("**Active Personas:**")
        for p in summary["personas"]:
            if p not in muted:
                weight = self.tracker.get_persona_weight(p)
                lines.append(f"  - {p} (weight: {weight:.2f})")

        return "\n".join(lines)


def main():
    """CLI for debate orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Debate orchestrator for parallel mode")
    parser.add_argument("--init", nargs=4, metavar=("TICKER", "TIMEFRAME", "MODEL", "MODE"),
                       help="Initialize a new debate")
    parser.add_argument("--personas", nargs="+", help="List of personas")
    parser.add_argument("--status", action="store_true", help="Show debate status")
    parser.add_argument("--convergence", action="store_true", help="Check convergence")
    parser.add_argument("--weights", nargs="+", help="Get persona weights")
    parser.add_argument("--mute-check", nargs="+", help="Check which personas would be muted")

    args = parser.parse_args()

    orchestrator = DebateOrchestrator()

    if args.init:
        ticker, timeframe, model, mode = args.init
        personas = args.personas or [
            "Trend Architect",
            "Tape Reader / Volume Profile",
            "Risk Manager",
            "Short-Seller"
        ]

        debate_id = orchestrator.start_debate(ticker, timeframe, model, personas, mode)
        print(f"Debate started: ID={debate_id}")
        print(f"Personas: {', '.join(personas)}")
        print(f"Mode: {mode}")

    elif args.status:
        print(orchestrator.get_status_display())

    elif args.convergence:
        conv = orchestrator.check_convergence()
        print(f"Converged: {conv['converged']}")
        print(f"Verdict: {conv['verdict']}")
        print(f"Confidence: {conv['confidence']:.2%}")
        print(f"Reason: {conv['reason']}")

    elif args.weights:
        tracker = PersonaTracker()
        weights = tracker.get_all_weights(args.weights)
        print("\n=== Persona Weights ===\n")
        for persona, weight in sorted(weights.items(), key=lambda x: -x[1]):
            print(f"  {persona}: {weight:.2f}")

    elif args.mute_check:
        scorer = ChallengeScorer()
        print("\n=== Mute Check ===\n")
        for persona in args.mute_check:
            success_rate, total = orchestrator.tracker.get_challenge_success_rate(persona)
            should_mute = orchestrator.tracker.should_mute_persona(persona)
            print(f"  {persona}: {success_rate:.1%} success ({total} challenges) - "
                  f"{'MUTED' if should_mute else 'ACTIVE'}")


if __name__ == "__main__":
    main()
