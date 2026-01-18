# Ask Skill Reference

Detailed operations for ask history management.

## History Operations

### Read History

```bash
# Returns null if file doesn't exist
cat ask-history/{TICKER}.json
```

### Filter Rules

| Status | Condition | Action |
|--------|-----------|--------|
| `answered` | Always | SKIP - use cached |
| `pending` | Always | SKIP - awaiting response |
| `unavailable` | `retry_after > NOW` | SKIP - in retry window |
| `unavailable` | `retry_after <= NOW` | ASK - retry expired |
| Not found | N/A | ASK - new question |

### Record New Question

```json
{
  "id": "q_20250118_001",
  "question": "What is NVDA's institutional ownership?",
  "category": "fundamental",
  "asked_at": "2025-01-18T10:30:00Z",
  "status": "pending",
  "tags": ["benchmark_gate_q3"],
  "related_skill": "trading-plan"
}
```

### Update After Response

| User Response | Status | Action |
|---------------|--------|--------|
| Provides answer | `answered` | Store answer, `answered_at=NOW` |
| "unavailable", "don't know" | `unavailable` | `retry_after=+30d`, `ask_count++` |
| Partial answer | `answered` | Create follow-up |

## Categories

| Category | Description | Example |
|----------|-------------|---------|
| `fundamental` | Business metrics, financials | "What is P/E ratio?" |
| `technical` | Price action, indicators | "What is RSI level?" |
| `catalyst` | Upcoming events | "Any earnings in next 10 days?" |
| `sentiment` | Social, institutional flow | "What is social sentiment?" |
| `benchmark` | Benchmark Gate data | "Beating sector ETF?" |
| `system` | Workflow issues | "Run /analyze first" |

## Self-Answerable vs. User-Only Questions

**Self-Answerable (use files, scripts, or web search instead):**

| Question Type | How to Answer |
|---------------|---------------|
| "What is current price?" | `python scripts/get_price.py TICKER` |
| "What is P/E ratio?" | `analytics/{TICKER}/fundamental_analysis.md` or web search |
| "What are recent earnings?" | `news/{TICKER}/` or web search |
| "What sector is TSLA in?" | Web search or fundamental analysis |
| "Who are competitors?" | Web search or fundamental analysis |
| "What is RSI level?" | `analytics/{TICKER}/technical_analysis.md` |

**User-Only (these justify /ask invocation):**

| Question Type | Why User Only |
|---------------|---------------|
| "What was your original buy rationale?" | Personal context not in files |
| "What is your target exit price?" | User's personal preference |
| "What risk tolerance applies?" | User's personal situation |
| "Is this for retirement or taxable?" | User's personal context |
| "What trading platform do you use?" | User's personal setup |

## Skill Integration Patterns

### trading-plan Gaps

| Benchmark | Question |
|-----------|----------|
| Q1: Alpha Source | "What is {TICKER}'s specific competitive edge?" |
| Q2: Relative Strength | "Is {TICKER} beating its sector ETF over 3M?" |
| Q3: Institutional | "What is institutional ownership trend?" |
| Q4: Anti-Catalyst | "Any major events in next 10 days?" |
| Q5: Sentiment | "What is current social sentiment?" |

### trading-debate Gaps

| Gap | Question |
|-----|----------|
| Catalysts | "What are top 3 upcoming catalysts in 6 months?" |
| Machine type | "HYPE/EARNINGS/MEAN_REVERSION - which fits?" |
| Bear case | "What is primary bear case risk?" |
| Sector | "What sector and top 3 competitors?" |

### position-review Gaps

| Gap | Question |
|-----|----------|
| Machine type | "What was original machine classification?" |
| Entry rationale | "What was original buy rationale?" |
| Fundamental score | "What is current fundamental score (0-100)?" |
| Thesis status | "Has thesis been validated (yes/no/pending)?" |

### watchlist_manager Gaps

| Gap | Question |
|-----|----------|
| Strategy | "What trading strategy fits these technicals?" |
| Fit score | "What indicators suggest fit >= 60?" |
| Trading levels | "What are support/resistance levels?" |
| Sector | "What sector and industry?" |

## Retry Logic

After 3 attempts with `unavailable`:
- Consider marking as `permanently_unavailable`
- Skip future questions on this topic

## JSON Schema

See `ask-history/README.md` for complete schema.
