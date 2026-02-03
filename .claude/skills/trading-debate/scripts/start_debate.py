#!/usr/bin/env python3
"""
Start a trading debate session.
1. Validates analytics freshness
2. Parses timeframe & selects model
3. Checks macro thesis
4. Determines mode (fast/parallel/sequential)
5. Generates debate file structure with optimization features
6. Outputs context for LLM to start debate

Enhanced with game-theoretic optimizations:
- Fast mode for scalping (1d-3d)
- Parallel challenge mode (default)
- Bayesian confidence tracking
- Persona accuracy weighting
"""
import argparse
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Import siblings
try:
    from parse_timeframe import parse_timeframe
    from validate_analytics import validate_analytics
except ImportError:
    # Handle if run from different dir
    sys.path.append(str(Path(__file__).parent))
    from parse_timeframe import parse_timeframe
    from validate_analytics import validate_analytics

# Load config
def load_config():
    """Load configuration from config.json."""
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "modes": {
            "scalping_fast_threshold_days": 3,
            "default_mode": "parallel"
        }
    }


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".claude").exists():
             return parent
    return Path.cwd()


def get_latest_macro(root: Path):
    macro_dir = root / 'macro' / 'theses'
    if not macro_dir.exists():
        return None

    files = sorted(macro_dir.glob('macro_thesis_*.md'), reverse=True)
    if files:
        return files[0]
    return None


def determine_mode(tf_data: dict, config: dict, force_mode: str = None) -> str:
    """
    Determine debate mode based on timeframe and config.

    Args:
        tf_data: Parsed timeframe data
        config: Configuration dict
        force_mode: Override mode if specified

    Returns:
        Mode: "fast", "parallel", or "sequential"
    """
    if force_mode:
        return force_mode

    days = tf_data.get('days', 0)
    model = tf_data.get('model_name', '')

    # Fast mode for 1d-3d scalping
    fast_threshold = config.get('modes', {}).get('scalping_fast_threshold_days', 3)
    if days <= fast_threshold and 'scalping' in model.lower():
        return 'fast'

    # Default from config
    return config.get('modes', {}).get('default_mode', 'parallel')


def get_personas_for_mode(model: str, mode: str) -> list:
    """Get list of personas for the given model and mode."""
    config = load_config()

    if mode == 'fast':
        return config.get('personas', {}).get('fast', [
            "Trend Architect",
            "Tape Reader / Volume Profile",
            "Risk Manager"
        ])

    # For other modes, use model-specific personas
    model_key = model.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
    personas = config.get('personas', {}).get(model_key)

    if personas == 'all':
        return config.get('personas', {}).get('all', [
            "Macro Strategist",
            "Sentiment & Flow Analyst",
            "Trend Architect",
            "Mean-Reversion Specialist",
            "Fundamental Catalyst",
            "Statistical Quant",
            "Tape Reader / Volume Profile",
            "Short-Seller",
            "Risk Manager"
        ])

    if isinstance(personas, list):
        return personas

    # Default fallback
    return config.get('personas', {}).get('all', [])


# Template for standard parallel/sequential mode
STANDARD_TEMPLATE = """# {ticker} Trading Debate ({timeframe})

**Date:** {date}
**Model:** {model_name}
**Timeframe:** {days} days
**Mode:** {mode}
**Agents:** {agents}
**Macro Context:** {macro_file}

---

## Game-Theoretic Optimizations Active

- **Bayesian Confidence Tracking:** Enabled
- **Persona Accuracy Weighting:** {weighting_enabled}
- **Parallel Challenge Mode:** {parallel_enabled}
- **Auto-Muting:** {mute_enabled}

---

## 1. Opening Statements

Each analyst provides their evaluation ({word_count} words):

{personas_section}

### Phase 1 Instructions

{phase1_instructions}

## 2. Adversarial Rebuttal (Parallel Mode)

### Round 1 Challenges

{round1_instructions}

## 3. Bayesian Confidence Tracker

| Round | P(Buy) | P(Sell) | Confidence | Change |
|-------|--------|---------|------------|--------|
| -     | -      | -       | -          | -      |

## 4. CIO Synthesis & Verdict

**Verdict:** [BUY/SELL/WATCH/AVOID]
**Conviction:** [HIGH/MEDIUM/LOW]
**Confidence Level:** [0-100%]

### Key Bull Points
1.
2.
3.

### Key Bear Points
1.
2.
3.

### Risk Assessment
-

### Execution Plan
- **Entry Zone:**
- **Target:**
- **Stop-Loss:**
- **Position Size:**
- **Duration:**

---

## Debate Metadata

- **Debate ID:** {debate_id}
- **Challenges Issued:** 0
- **Challenges Successful:** 0
- **Rounds Completed:** 0
- **Final Confidence:** N/A

"""

# Template for fast mode
FAST_TEMPLATE = """# {ticker} Fast Mode Debate ({timeframe})

**Date:** {date}
**Mode:** Fast (3 agents, 1 round optimized for scalping)
**Timeframe:** {days} days
**Macro Context:** {macro_file}

---

## 1. Rapid Analysis (100 words each)

### Trend Architect

**Focus:** Intraday trend structure, EMA alignment, momentum direction

**Your Analysis:**
[Provide 100-word assessment]

### Tape Reader / Volume Profile

**Focus:** Volume profile, entry timing, smart money detection

**Your Analysis:**
[Provide 100-word assessment]

### Risk Manager

**Focus:** Stop distance, position size, R:R ratio

**Your Analysis:**
[Provide 100-word assessment]

---

## 2. Challenge Phase

Each agent challenges ONE other agent (100 words max).

**Challenge Format:**
```
CHALLENGE_TO: [Agent]
DISAGREEMENT: [What you disagree with]
COUNTER_EVIDENCE: [Your reasoning]
```

### Challenges

**Trend Architect challenges:** [ ]
**Tape Reader challenges:** [ ]
**Risk Manager challenges:** [ ]

---

## 3. Response Phase

Each agent responds to challenges (150 words max).

### Responses

**Trend Architect responds:** [ ]
**Tape Reader responds:** [ ]
**Risk Manager responds:** [ ]

---

## 4. CIO Verdict

**Action:** [BUY/SELL/SKIP]
**Conviction:** [HIGH/MEDIUM/LOW]
**Entry Zone:** [ ]
**Target:** [ ]
**Stop:** [ ]
**Position Size:** [% of equity, max 0.5%]

**Reasoning:**
[Summarize the decision]

---

## Debate Metadata

- **Mode:** Fast (no voting phase)
- **Agents:** 3
- **Rounds:** 1
"""


def generate_persona_section(personas: list) -> str:
    """Generate the personas section for the template."""
    sections = []
    for i, persona in enumerate(personas, 1):
        sections.append(f"""
### {i}. {persona}

**Analysis:** [Your evaluation here]
""")
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(
        description='Start a trading debate with game-theoretic optimizations.'
    )
    parser.add_argument('ticker', help='Stock ticker')
    parser.add_argument('timeframe', help='Timeframe (e.g., 3d, 2w, 6m, 1y)')
    parser.add_argument('--mode', choices=['auto', 'fast', 'parallel', 'sequential'],
                       default='auto', help='Debate mode (default: auto)')
    parser.add_argument('--sequential', action='store_true',
                       help='Use sequential mode (alias for --mode sequential)')

    args = parser.parse_args()
    ticker = args.ticker.upper()

    print(f"Initializing Trading Debate for {ticker} ({args.timeframe})...")
    print("-" * 50)

    # 1. Parse Timeframe
    tf_data = parse_timeframe(args.timeframe)
    if "error" in tf_data:
        print(f"Error: {tf_data['error']}")
        sys.exit(1)

    print(f"✓ Model: {tf_data['model_name']} ({tf_data['agents']} agents)")

    # 2. Validate Analytics
    print(f"Checking analytics...")
    analytics_res = validate_analytics(ticker)

    if not analytics_res['valid']:
        print(f"✗ Analytics validation failed for {ticker}")
        for err in analytics_res['errors']:
            print(f"  - {err}")
        print("\nRun: /analyze {ticker} first")
        sys.exit(1)

    for warning in analytics_res['warnings']:
        print(f"  ! {warning}")

    print("✓ Analytics files present")

    # 3. Macro Check
    root = get_project_root()
    macro_file = get_latest_macro(root)
    macro_name = "None"
    if macro_file:
        macro_name = macro_file.name
        print(f"✓ Macro Context: {macro_name}")
    else:
        print("! No macro thesis found (using neutral assumption)")

    # 4. Determine Mode
    config = load_config()
    force_mode = args.mode if args.mode != 'auto' else None
    if args.sequential:
        force_mode = 'sequential'

    mode = determine_mode(tf_data, config, force_mode)
    print(f"✓ Mode: {mode.upper()}")

    # 5. Get Personas
    personas = get_personas_for_mode(tf_data['model_name'], mode)
    print(f"✓ Agents: {len(personas)} personas")

    # 6. Generate Debate ID
    import time
    debate_id = int(time.time())

    # 7. Generate File
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = root / 'trading-debates' / ticker
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{ticker}_{date_str.replace('-','_')}_{args.timeframe}.md"
    output_path = output_dir / filename

    if mode == 'fast':
        content = FAST_TEMPLATE.format(
            ticker=ticker,
            timeframe=args.timeframe,
            date=date_str,
            days=tf_data['days'],
            macro_file=macro_name
        )
        word_count = "100"
        parallel_enabled = "N/A"
        phase1_instructions = """
Each agent provides concise analysis (100 words max):
- Trend Architect: EMA stack, higher highs/lows, momentum
- Tape Reader: Volume vs average, entry timing, liquidity
- Risk Manager: ATR stop, R:R ratio, position size
"""
    else:
        word_count = "150-200" if mode == "parallel" else "200-250"
        parallel_enabled = "Yes" if mode == "parallel" else "No"
        mute_enabled = "Yes" if mode == "parallel" else "No"

        personas_section = generate_persona_section(personas)

        phase1_instructions = f"""
Each analyst provides evaluation ({word_count} words):

**Environment Context:**
- Macro Strategist: Market regime, tailwinds/headwinds
- Sentiment & Flow: Crowd positioning, contrarian signals

**Directional Bias:**
- Trend Architect: Trend structure, momentum alignment
- Mean-Reversion Specialist: Overbought/oversold extremes
- Fundamental Catalyst: Earnings, guidance, events

**Evidence Validation:**
- Statistical Quant: Z-scores, volatility, probability
- Tape Reader: Volume confirmation, divergence detection

**Capital Preservation:**
- Short-Seller: Red-teaming, structural flaws
- Risk Manager: R:R, position sizing, correlation

**Challenge Format:**
```
CHALLENGE_TO: [Persona Name]
WHAT_I_DISAGREE_WITH: [Specific claim]
COUNTER_EVIDENCE: [Your reasoning]
```
"""

        content = STANDARD_TEMPLATE.format(
            ticker=ticker,
            timeframe=args.timeframe,
            date=date_str,
            model_name=tf_data['model_name'],
            days=tf_data['days'],
            mode=mode.upper(),
            agents=len(personas),
            macro_file=macro_name,
            weighting_enabled="Yes (after 10 debates)",
            parallel_enabled=parallel_enabled,
            mute_enabled=mute_enabled,
            debate_id=debate_id,
            personas_section=personas_section,
            word_count=word_count,
            phase1_instructions=phase1_instructions,
            round1_instructions=f"""
Each persona issues exactly ONE challenge to another persona.

**Key Rules:**
- Challenge the persona you disagree with MOST
- Be specific about WHAT you disagree with
- Provide counter-evidence or reasoning
- Maximum 100 words per challenge

**Active Personas:** {', '.join(personas)}
"""
        )

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✓ Created debate file: {output_path.relative_to(root)}")
    print("-" * 50)
    print("READY TO START DEBATE")
    print(f"Debate ID: {debate_id}")
    print(f"Mode: {mode.upper()}")
    print(f"Agents: {len(personas)}")

    if mode == 'fast':
        print("\nFast Mode Instructions:")
        print("  - 3 agents: Trend Architect, Tape Reader, Risk Manager")
        print("  - 1 round only")
        print("  - CIO decides directly (no voting phase)")
    else:
        print("\nParallel Mode Instructions:")
        print(f"  - {len(personas)} agents issue challenges simultaneously")
        print("  - Muted personas (<30% challenge success) skip remaining rounds")
        print("  - Bayesian confidence tracker updates each round")
        print("  - Early stop when confidence >90%")

    print(f"\nRefer to analytics/{ticker}/ and {macro_name} for data.")


if __name__ == '__main__':
    main()
