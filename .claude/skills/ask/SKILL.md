---
name: ask
description: Generate factual questions about a ticker with intelligent history tracking to avoid duplicates. Auto-triggered by decision skills (trading-plan, trading-debate, position-review, watchlist_manager) when data gaps detected. Also invoked directly via /ask {TICKER} command.
allowed-tools: Read, Write, Bash
---

# Ask Skill

Generate up to 5 high-value, fact-based questions about a ticker to bridge information gaps for investment decisions. Tracks history to avoid redundant questions.

## Quick Start

**Direct invocation:**
```bash
/ask NVDA
```

**Auto-triggered by skills:**
- trading-plan: Benchmark Gate failures
- trading-debate: Missing catalysts/thesis
- position-review: Ambiguous machine type
- watchlist_manager: Strategy unclear

## Workflow

1. **Check history** - Read `ask-history/{TICKER}.json`
2. **Filter** - Skip answered/unavailable-in-window questions
3. **Self-answerable check** - Skip if answerable via files or web search
4. **Generate** - Create max 5 new questions (only unanswerable ones)
5. **Present** - Show questions to user
6. **Update** - Save responses to history

## Self-Answerable Filter

**DO NOT ask the user if you can find the answer yourself:**

| Source | Check First |
|--------|-------------|
| **Existing files** | `analytics/{TICKER}/`, `news/{TICKER}/`, `trading-plans/{TICKER}/` |
| **Web search** | Use `WebSearch` for factual, public information |
| **Scripts** | Run `fetch_prices.py`, `get_fundamental.py`, etc. |

**Only ask the user for:**
- Private/proprietary data not publicly available
- Personal investment rationale/context
- Qualitative judgments requiring human preference
- Data confirmed unavailable via web search

## Question Constraints

- **< 300 words** total output
- **Verifiable facts only** - no predictions/speculation
- **Categories**: fundamental, technical, catalyst, sentiment, benchmark, system
- **Format**: Bullet points only — DO NOT use tables for question presentation

## History Status Flow

```
NEW → PENDING → (answered OR unavailable)
                      ↓          ↓
                   use cache   retry_after +30d
```

| Status | Action |
|--------|--------|
| `answered` | Use cached answer |
| `pending` | Awaiting response |
| `unavailable` | Re-ask after retry_after date |

## Additional Resources

- **Schema & Examples**: [REFERENCE.md](REFERENCE.md)
- **History Storage**: `ask-history/README.md`

## Configuration

Defaults (override in `.claude/settings.local.json`):
```json
{
  "ask_history": {
    "retry_days": 30,
    "max_attempts": 3,
    "batch_size": 5
  }
}
```
