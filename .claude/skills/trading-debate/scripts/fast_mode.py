#!/usr/bin/env python3
"""
Fast Mode - Optimized debate for scalping (1d-3d timeframes).

Uses only 3 critical agents for rapid decision-making:
1. Trend Architect - Direction and momentum
2. Tape Reader - Volume validation and entry timing
3. Risk Manager - R:R guardrails

Single round of challenges, CIO decides directly (no voting phase).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class FastModeAgent(Enum):
    """The 3 agents used in fast mode."""
    TREND_ARCHITECT = "Trend Architect"
    TAPE_READER = "Tape Reader / Volume Profile"
    RISK_MANAGER = "Risk Manager"


@dataclass
class FastModeInput:
    """Input data for fast mode analysis."""
    ticker: str
    timeframe: str
    price: float
    ema_20: float
    ema_50: float
    ema_200: float
    rsi: float
    volume_avg: int
    volume_today: int
    atr: float
    support: float
    resistance: float


@dataclass
class FastModeAnalysis:
    """Analysis result from a single agent."""
    agent: str
    stance: str  # BULLISH, BEARISH, NEUTRAL
    reasoning: str
    confidence: float  # 0-1


@dataclass
class FastModeVerdict:
    """Final verdict from fast mode debate."""
    action: str  # BUY, SELL, SKIP
    conviction: str  # HIGH, MEDIUM, LOW
    entry_zone: str
    target: str
    stop: str
    position_size: float  # % of equity
    reasoning: str


class FastModeOrchestrator:
    """
    Orchestrates fast mode debates for scalping.

    Flow:
    1. Each agent provides 100-word take
    2. Each agent challenges one other (simultaneously)
    3. Agents respond (150 words max)
    4. CIO issues verdict (no voting phase)
    """

    # Agent prompts for LLM
    AGENT_PROMPTS = {
        FastModeAgent.TREND_ARCHITECT: """
Analyze the trend structure for a scalping trade:

**Your Focus (100 words max):**
- EMA stack alignment (20/50/200)
- Price position relative to EMAs
- Higher highs/lows or lower highs/lows
- Momentum direction

**Output format:**
```
STANCE: BULLISH/BEARISH/NEUTRAL
CONFIDENCE: 0-100
Reasoning: [your analysis]
```
""",
        FastModeAgent.TAPE_READER: """
Analyze volume and entry timing:

**Your Focus (100 words max):**
- Volume vs average (expanding or contracting?)
- Volume quality (spread, churn)
- Entry timing (smart money active?)
- Liquidity check

**Output format:**
```
STANCE: BULLISH/BEARISH/NEUTRAL
CONFIDENCE: 0-100
Reasoning: [your analysis]
```
""",
        FastModeAgent.RISK_MANAGER: """
Analyze risk/reward:

**Your Focus (100 words max):**
- ATR-based stop distance
- R:R ratio (minimum 3:1)
- Position size calculation
- Liquidity check

**Output format:**
```
STANCE: BULLISH/BEARISH/NEUTRAL
CONFIDENCE: 0-100
Entry: [price zone]
Target: [price level]
Stop: [price level]
Reasoning: [your analysis]
```
"""
    }

    def __init__(self):
        """Initialize fast mode orchestrator."""
        self.agents = list(FastModeAgent)
        self.analyses: List[FastModeAnalysis] = []

    def should_use_fast_mode(self, days: int) -> bool:
        """Determine if fast mode should be used based on timeframe."""
        return days <= 3

    def get_prompt_for_agent(self, agent: FastModeAgent, data: FastModeInput) -> str:
        """Get the full prompt for an agent including data."""
        base_prompt = self.AGENT_PROMPTS[agent]

        data_context = f"""
**Ticker:** {data.ticker}
**Timeframe:** {data.timeframe}
**Current Price:** ${data.price}
**EMA 20:** ${data.ema_20}
**EMA 50:** ${data.ema_50}
**EMA 200:** ${data.ema_200}
**RSI:** {data.rsi}
**Volume Today:** {data.volume_today:,} (Avg: {data.volume_avg:,})
**ATR:** ${data.atr}
**Support:** ${data.support}
**Resistance:** ${data.resistance}
"""
        return data_context + "\n" + base_prompt

    def get_challenge_prompt(self, analyses: List[FastModeAnalysis]) -> str:
        """Get the challenge phase prompt."""
        prompt = """
## Challenge Phase

Each agent must challenge ONE other agent's stance.

**Your Challenge (100 words max):**
1. Who you challenge
2. What you disagree with
3. Your counter-evidence

**Analyses to challenge:**

"""
        for analysis in analyses:
            prompt += f"\n**{analysis.agent}:** {analysis.stance} - {analysis.reasoning}\n"

        return prompt

    def get_response_prompt(self, challenges: List[str]) -> str:
        """Get the response phase prompt."""
        prompt = """
## Response Phase

Respond to challenges against you (150 words max).

**Challenges:**

"""
        for i, challenge in enumerate(challenges, 1):
            prompt += f"\n{i}. {challenge}\n"

        prompt += """

**Your Response:**
- If you concede: acknowledge and withdraw your point
- If you defend: provide evidence supporting your original stance
"""

        return prompt

    def get_cio_prompt(self, analyses: List[FastModeAnalysis],
                      challenges: List[str],
                      responses: List[str]) -> str:
        """Get the CIO verdict prompt."""
        prompt = """
## CIO Verdict - Fast Mode

Review the analyses, challenges, and responses. Issue your verdict.

**Analyses:**

"""
        for analysis in analyses:
            prompt += f"\n**{analysis.agent} ({analysis.stance}, {analysis.confidence}%):** {analysis.reasoning}\n"

        prompt += "\n**Challenges:**\n"
        for i, challenge in enumerate(challenges, 1):
            prompt += f"\n{i}. {challenge}\n"

        prompt += "\n**Responses:**\n"
        for i, response in enumerate(responses, 1):
            prompt += f"\n{i}. {response}\n"

        prompt += """
**Your Verdict:**

```
ACTION: BUY/SELL/SKIP
CONVICTION: HIGH/MEDIUM/LOW
ENTRY: [price zone]
TARGET: [price level]
STOP: [price level]
POSITION_SIZE: [% of equity, 0.25-0.5% max]

Reasoning: [summary of why this makes sense]
```

**Consider:**
- Trend Architect's direction
- Tape Reader's volume validation
- Risk Manager's R:R assessment
- Any conceded points
"""

        return prompt

    def parse_analysis(self, agent: str, response: str) -> FastModeAnalysis:
        """Parse agent response into FastModeAnalysis."""
        lines = response.strip().split('\n')

        stance = "NEUTRAL"
        confidence = 0.5
        reasoning = response

        for line in lines:
            if line.startswith("STANCE:"):
                stance = line.split(":", 1)[1].strip().upper()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip()) / 100
                except:
                    confidence = 0.5
            elif line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()

        return FastModeAnalysis(
            agent=agent,
            stance=stance,
            reasoning=reasoning,
            confidence=confidence
        )

    def get_template(self) -> str:
        """Get the fast mode debate template."""
        return """# {TICKER} Fast Mode Debate ({TIMEFRAME})

**Date:** {DATE}
**Mode:** Fast (3 agents, 1 round)

## Agent Analyses

### Trend Architect
{ANALYSIS_TREND}

### Tape Reader
{ANALYSIS_VOLUME}

### Risk Manager
{ANALYSIS_RISK}

## Challenges

{CHALLENGE_TREND}
{CHALLENGE_VOLUME}
{CHALLENGE_RISK}

## Responses

{RESPONSE_TREND}
{RESPONSE_VOLUME}
{RESPONSE_RISK}

## CIO Verdict

{VERDICT}
"""


def main():
    """CLI for fast mode operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Fast mode for scalping debates")
    parser.add_argument("--check", type=int, help="Check if timeframe uses fast mode (days)")
    parser.add_argument("--template", action="store_true", help="Show debate template")

    args = parser.parse_args()

    orchestrator = FastModeOrchestrator()

    if args.check is not None:
        uses_fast = orchestrator.should_use_fast_mode(args.check)
        print(f"Timeframe: {args.check} days")
        print(f"Fast Mode: {'YES' if uses_fast else 'NO'}")

    elif args.template:
        print(orchestrator.get_template())


if __name__ == "__main__":
    main()
