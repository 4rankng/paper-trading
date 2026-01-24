---
name: debate
description: Multi-agent truth-seeking debate for macroeconomic, geopolitical, and policy analysis. Uses adversarial reasoning to uncover causal mechanisms and predict outcomes. Use for: "Will Fed cut rates?", "Will trade war escalate?", "Policy impact analysis", "Election outcomes", "Geopolitical forecasting".
allowed-tools:
  - Read
  - Bash(python:*)
  - Bash(ls:*)
  - mcp__web-search-prime__webSearchPrime
  - mcp__web-reader__webReader
  - mcp__reddit__fetch_reddit_hot_threads
  - mcp__memory__*
context: fork
agent: general-purpose
---

# Truth-Seeking Macro Debate

Multi-agent adversarial reasoning engine designed to uncover truth, understand causal mechanisms, and predict real-world outcomes.

## Philosophy

**The goal is truth, not consensus.**

This skill uses structured adversarial debate to:
1. **Challenge assumptions** through diverse analytical lenses
2. **Expose weak reasoning** through systematic critique
3. **Converge on truth** by eliminating falsified positions
4. **Quantify uncertainty** where truth cannot be determined

## Quick Start

```
/debate [QUESTION]
```

**Examples of good questions:**
- `/debate Will the Fed cut rates by 25bp in January 2026?`
- `/debate Will US-China trade relations deteriorate further in 2026?`
- `/debate What is the probability of a US recession in 2026?`
- `/debate Will AI regulation pass Congress this year?`

**Note:** Questions should be about *what will happen* and *why*, not *what should we do*.

## When to Use

| Purpose | Use This | NOT This |
|---------|----------|----------|
| **Understand causality** | `debate` | - |
| **Predict outcomes** | `debate` | - |
| **Analyze policy impact** | `debate` | - |
| **Geopolitical forecasting** | `debate` | - |
| **Trading decisions** | `trading-debate` | `debate` |
| **Portfolio management** | `portfolio_manager` | `debate` |

## Debate vs. Trading Debate

| Aspect | Macro Debate | Trading Debate |
|--------|-------------|----------------|
| **Goal** | Uncover truth, predict outcomes | Generate alpha, decide trades |
| **Output** | Probability-weighted scenarios | Buy/sell/hold signals |
| **Timeframe** | Months to years | Days to weeks |
| **Focus** | Causal mechanisms, structural factors | Price action, market timing |
| **Personas** | Domain experts, policymakers | Market analysts, traders |

## Reference Files

All execution details are in the `references/` folder:

| File | Purpose |
|------|---------|
| `personas.md` | 18 expert personas with analytical frameworks |
| `workflows.md` | 8-step truth-seeking workflow |
| `constraints.md` | Position structure, challenge protocols, falsifiability |
| `quality-gates.md` | Question validation, prediction quality standards |
| `synthesis-format.md` | Prediction output template |

## Truth-Seeking Workflow

1. **Define Question** → Falsifiable, time-bounded, outcome-focused
2. **Select Personas** → Diverse analytical frameworks, adversarial positions
3. **Gather Evidence** → Shared facts, multiple perspectives
4. **Position Generation** → Each with causal mechanism and falsification criteria
5. **Challenge Rounds** → Attack assumptions, evidence, and logic
6. **Track Convergence** → Eliminate falsified positions, identify consensus
7. **Synthesize** → Probability-weighted prediction with scenarios
8. **Calibrate** → Track accuracy over time

## Key Principles

1. **Falsifiability First** - Every position must specify what would prove it wrong
2. **Causal Depth** - Understand *why* something will happen, not just *what*
3. **Adversarial Diversity** - Include opposing analytical frameworks
4. **Convergence as Signal** - High consensus on a claim increases confidence
5. **Embrace Uncertainty** - Low-confidence truth is better than false confidence
6. **Calibration Over Confidence** - Track prediction accuracy, not just being "right"

## Expected Outcome

A debate succeeds when it produces:
- **Clear prediction** with probability assessment
- **Causal mechanism** explaining *why* the outcome is likely
- **Alternative scenarios** with triggering conditions
- **Monitoring framework** to track leading indicators
- **Critical uncertainties** that would change the conclusion

## Prerequisites

Before debating, check current macro stance:
```bash
ls -lt macro/theses/ | head -5
```

## Output Format

Use **role titles only**, never persona names:
- Correct: "Realist International Relations Scholar", "Central Banker"
- Incorrect: "DR. JOHN SMITH - Realist International Relations Scholar"
