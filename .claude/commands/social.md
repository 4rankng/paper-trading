---
name: social
description: Multi-agent conversation for stock discussion. Agents with different perspectives (Technical, Fundamental, Thesis, Risk) discuss freely.
argument-hint: [TICKER] [-t "topic"] [--turns N]
disable-model-invocation: true
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
  - Skill(agent-social)
  - Skill(analytics_generator)
---

Multi-agent conversation for stock discussion. 4 AI agents (Tech, Fund, Sent, Risk) discuss freely.

## Usage

```
/social [TICKER] [OPTIONS]
```

## Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `TICKER` | Stock symbol (required) | NVDA, COIN, TSLA |
| `-t "topic"` | Initial topic/question (optional) | "-t Is this a bounce?" |
| `--turns N` | Max turns (optional, default: 50) | "--turns 20" |

## Examples

```
/social NVDA
/social COIN -t "Is this a bounce or dead cat?"
/social TSLA --turns 15
```

## What Happens

1. Loads analytics for the stock (if available)
2. 4 agents discuss: Tech (charts), Fund (fundamentals), Sent (sentiment), Risk (downside)
3. Conversation displayed live in terminal
4. Ends naturally via #GOODBYE consensus
5. Saved to `social-conversations/[TICKER]/`

## Agents

| Agent | Perspective |
|-------|-------------|
| **Tech** | Charts, patterns, indicators, price action |
| **Fund** | Business quality, valuation, growth |
| **Sent** | News flow, buzz, momentum |
| **Risk** | Downside, volatility, red flags |

## Output

- Live terminal: Real-time conversation
- `social-conversations/[TICKER]/conversation_YYYYMMDD_HHMMSS.jsonl` - Full transcript
- `social-conversations/[TICKER]/summary_YYYYMMDD_HHMMSS.md` - Human-readable summary

## When to Use

| Use Case | Command |
|----------|---------|
| Explore ideas about a stock | `/social NVDA` |
| Get diverse perspectives | `/social COIN` |
| Discover blind spots | `/social TSLA` |
| Free-form discussion | `/social AAPL -t "Earnings prep?"` |

## NOT For

- Trading signals → Use `/trade`
- Portfolio decisions → Use `portfolio_manager` skill
- Formal debate → Use `/debate`
- Structured analysis → Use `/analyze`

## Prerequisites

Recommended (not required): Analytics data exists
```
analytics/[TICKER]/technical.md
analytics/[TICKER]/fundamental.md
analytics/[TICKER]/thesis.md
```

If missing, agents discuss based on general knowledge. Create with `/analyze [TICKER]`.

## Stopping

- Agents self-terminate via #GOODBYE consensus
- Or: Ctrl+C to interrupt
- Or: Reaches turn limit

## Execution

Execute `agent-social` skill with the ticker argument:
1. Parse ticker and options
2. Execute: `python scripts/social_conversation.py [TICKER] [OPTIONS]`
3. Display output
