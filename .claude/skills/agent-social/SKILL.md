---
name: agent-social
description: Multi-agent conversation for stock discussion. Agents with different perspectives (Technical, Fundamental, Thesis, Risk) discuss freely. Use for: "social conversation", "agent discussion", "free-form stock talk".
allowed-tools:
  - Bash(python:*)
  - Read
  - Glob
  - WebSearch
context: fork
agent: general-purpose
---

# Agent-Social Skill

Multi-agent conversation system where AI agents with different analytical perspectives discuss a stock freely.

## Quick Start

```
/social [TICKER]
```

Example: `/social NVDA`

## What It Does

Spawns 4 AI agents that discuss a stock:

| Agent | Focus |
|-------|-------|
| **Tech** | Charts, patterns, indicators, price action |
| **Fund** | Business quality, fundamentals, valuation |
| **Thesis** | News, sentiment, mood, AND investment thesis |
| **Risk** | Downside, volatility, what could go wrong |

## How It Works

1. **Checks analytics freshness** for the stock
2. **Web searches** for fresh data (last 24-48h)
3. **Loads analytics** (technical.md, fundamental.md, thesis.md if available)
4. **Spawns 4 agents** via Claude Code CLI (no API keys needed)
5. **Agents take turns** discussing the stock WITH fresh data
6. **Ends naturally** when agents reach #GOODBYE consensus
7. **Saves** conversation to `social-conversations/[TICKER]/`

## CRITICAL: Data-First Workflow

Before starting ANY agent conversation, you MUST:

### 1. Check Analytics Freshness
```bash
ls -lt analytics/{TICKER}/ | head -5
```

### 2. Web Search for Fresh Data (Last 24-48h)
Use `WebSearch` for:
- `{TICKER} stock news today` - Latest headlines
- `{TICKER} earnings guidance` - Recent guidance
- `{TICKER} analyst ratings` - Street sentiment
- `{TICKER} sector news` - Industry developments

### 3. Check Market Sentiment
- Fear & Greed: https://edition.cnn.com/markets/fear-and-greed

### 4. Feed Fresh Data to Agents
Pass the web search results via `--fresh-news` argument:
```bash
python scripts/social_conversation.py {TICKER} --fresh-news "{search_results}"
```

## Data Freshness Rules

| Condition | Action |
|-----------|--------|
| Analytics missing | Run `/analyze {TICKER}` first |
| Analytics >24h old | Run `/analyze {TICKER}` OR proceed with web search |
| Analytics <24h old | Proceed with web search for fresh context |

**WARNING: Agents MUST have fresh data. Do NOT skip web search.**

## Output

- **Live terminal**: Real-time conversation as it happens
- **JSONL log**: Full transcript for replay
- **Markdown summary**: Human-readable summary

## When to Use

| Use This | NOT This |
|----------|----------|
| Explore ideas about a stock | Trading signals (use /trade) |
| Get diverse perspectives | Portfolio decisions (use portfolio_manager) |
| Discover blind spots | Formal debate (use /debate) |
| Free-form discussion | Structured analysis (use /analyze) |

## Prerequisites

**Analytics data recommended** (but not required):
```
analytics/{TICKER}/technical.md
analytics/{TICKER}/fundamental.md
analytics/{TICKER}/thesis.md
```

If missing, agents will discuss based on general knowledge + web search results.

## Stopping Conditions

Conversation ends when:
- All agents say `#GOODBYE` (natural consensus)
- Agents repeat themselves (similarity > 75%)
- Turn limit reached (default: 50)
- User presses Ctrl+C

## Configuration

Edit `scripts/config/social_personas.yaml` to customize:
- Agent personas
- Max turns
- Delay between turns

## Examples

```
/social NVDA
/social COIN -t "Is this a bounce or dead cat?"
/social TSLA --turns 20
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Claude CLI not found" | Install Claude Code CLI |
| No analytics data | Run `/analyze [TICKER]` first (optional) |
| Stale analytics warning | Run `/analyze [TICKER]` or proceed with web search |
| Conversation too long | Use `--turns N` to limit |
| Agents repeating | Natural - will auto-terminate |

## Implementation

Core script: `scripts/social_conversation.py`

Adapted from agentic-social mediator pattern with:
- Stock-specific personas
- Analytics context injection
- Freshness checking
- Fresh data injection from web search
- JSONL persistence
- Markdown summaries
