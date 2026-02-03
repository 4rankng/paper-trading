# Trading Debate Workflows Reference

Detailed execution workflows for each trading model with game-theoretic optimizations.

---

## Debate Modes

| Mode | Description | Timeframe | Agents | Rounds | When to Use |
|------|-------------|-----------|--------|--------|-------------|
| **Fast** | 3 agents, 1 round, CIO direct verdict | 1d-3d | 3 | 1 | Quick scalps, intraday decisions |
| **Parallel** | Simultaneous challenges, O(n) efficiency | 1d-1y+ | 5-10 | 2-5 | Default for all timeframes |
| **Sequential** | Traditional back-and-forth | 1d-1y+ | 5-10 | 2-5 | Fallback for complex cases |

**Default:** Parallel mode (auto-selected by timeframe)

---

## Iteration Limits (Efficiency Control)

| Model | Max Rounds | Early Stop Condition |
|-------|------------|---------------------|
| Fast (1d-3d) | 1 round | N/A (single pass) |
| Scalping/Day (4d-7d) | 3 rounds | Confidence >90% OR no new evidence |
| Swing (1w-4w) | 5 rounds | Confidence >90% OR convergence |
| Position (1m-6m) | 5 rounds | Confidence >90% OR convergence |
| Investment (1y+) | 5 rounds | Confidence >90% OR convergence |

**Bayesian Early Convergence:**
- Stop when confidence interval <10% (P(buy) >90% or <10%)
- Minimum rounds apply (2 for scalping, 3 for others)
- Confidence stagnation (<5% change) also triggers stop

---

## Game-Theoretic Optimizations

### 1. Challenge Quality Scoring

| Outcome | Quality Score | Success | Description |
|---------|---------------|---------|-------------|
| Conceded | 1.0 | Yes | Target admits the point |
| Weak Defense | 0.5 | Yes | Target lacks evidence |
| Strong Defense | 0.0 | No | Target provides evidence |
| Irrelevant | -1.0 | No | Challenge ignored/off-topic |

**Persona Score:** `(successful_challenges × 2) - (concessions × 1) - (failed_challenges × 0.5)`

### 2. Auto-Muting

| Condition | Action |
|-----------|--------|
| Challenge success rate <30% | Persona muted for remaining rounds |
| Minimum 3 challenges issued | Before mute evaluation applies |
| Muted persona | Still votes in final phase |

### 3. Confidence Weighting

| Persona History | Vote Weight |
|-----------------|-------------|
| New (<10 debates) | 0.5 (baseline) |
| 75% accuracy | 0.75 |
| 40% accuracy | 0.40 |
| Perfect track record | 1.0 |

**Formula:** `weight = 0.5 + (accuracy - 0.5) × influence_factor`

### 4. Bayesian Confidence Tracker

After each round:
```
P(buy) = weighted_votes_for_buy / total_weighted_votes
confidence = |P(buy) - 0.5| × 2  # 0-1 scale
```

**Stop when:** `confidence > 0.90` AND `rounds >= minimum`

---

## Shared Components

These components are common to all trading models.

### Parallel Challenge-Response Mode (NEW)

#### Phase 2A: Simultaneous Challenge Issuing

Each persona X reviews all analyst answers and issues **ONE challenge** to the persona they disagree with most.

**Challenge Format:**
```
CHALLENGE_TO: [Persona Name]
WHAT_I_DISAGREE_WITH: [Specific claim]
COUNTER_EVIDENCE: [Your reasoning]
```

All challenges are issued **simultaneously** - no waiting for others.

#### Phase 2B: Batched Responses

Challenges are **grouped by target persona**:

```
## Challenges to Trend Architect

**Short-Seller challenges:** The EMA stack is weakening...
**Risk Manager challenges:** Stop distance too wide...

[Respond to all challenges above]
```

Each persona responds to **all their challenges at once** (150 words max).

#### Phase 2C: Scoring and Muting

1. Each challenge is scored (see [Challenge Quality Scoring](#1-challenge-quality-scoring))
2. Persona challenge success rates updated
3. Personas below 30% threshold are **muted**
4. Muted personas sit out remaining rounds (still vote in Phase 3)

#### Phase 2D: Iteration

Repeat rounds until:
- **Confidence >90%** (Bayesian convergence), OR
- **Max rounds completed**, OR
- **Confidence stagnates** (<5% change over 2 rounds)

### Legacy Sequential Mode (Fallback)

If parallel mode is disabled (`--sequential` flag), use traditional back-and-forth:

#### Step 2.1: Initial Challenges
Each persona challenges one other sequentially.

#### Step 2.2: Response and Justification
Challenged persona responds with justification or concession.

#### Step 2.3: Iteration
Continue rounds until convergence or max rounds.

### Shared Debate Rules

- **Must challenge**: Each persona must challenge at least one other
- **Must respond**: Challenged personas must always respond
- **Specific challenges**: Generic challenges penalized
- **Evidence-based**: Reference analytics data
- **Good faith**: Concede when cannot justify

### Phase 3: Holistic Confidence Vote (All Models)

After debate concludes, each analyst evaluates:

- All original analyst answers
- All challenges and responses
- All conceded points
- Remaining unresolved disputes

**Scoring 1-10:**
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Weighted Voting:**
- Votes weighted by historical accuracy (see [Confidence Weighting](#3-confidence-weighting))
- New personas: equal weight (0.5)
- Track record personas: weighted 0.1-1.0

**Voting Guidance:**
- Vote for **most well-defended** position
- Penalize positions that conceded
- Reward successful defenses
- **Contrarian Edge**: Lone dissent with strong evidence = "Watch", not "Avoid"

---

## Fast Mode Workflow (1d - 3d Scalping)

**Agents:** 3 personas (no voting phase, CIO direct verdict)
- Trend Architect
- Tape Reader / Volume Profile
- Risk Manager

### Phase 1: Rapid Analysis (100 words each)

**Trend Architect:**
- EMA stack alignment (20/50/200)
- Higher highs/lows or lower highs/lows
- Momentum direction

**Tape Reader:**
- Volume vs average
- Entry timing
- Liquidity check

**Risk Manager:**
- ATR stop distance
- R:R ratio (min 3:1)
- Position size (0.25-0.5% max)

### Phase 2: Challenge Round

Each agent challenges ONE other (100 words max):
```
CHALLENGE_TO: [Agent]
DISAGREEMENT: [What you disagree with]
COUNTER_EVIDENCE: [Your reasoning]
```

### Phase 3: Response Round

Each agent responds (150 words max):
- If conceding: "I concede on [point] because..."
- If defending: "The evidence shows..."

### Phase 4: CIO Verdict (No Voting)

**Action:** BUY/SELL/SKIP
**Conviction:** HIGH/MEDIUM/LOW
**Entry:** [price zone]
**Target:** [price level]
**Stop:** [price level]
**Position Size:** [% of equity, max 0.5%]

**Output includes:**
- Entry zone (market or limit near support)
- Target (1-2% moves for scalps)
- Stop-loss (1-1.5x ATR)
- Duration: Same day to 3 days
- Time stop: Exit EOD if no movement

---

## Scalping/Day Trading Model (4d - 7d): 4-Phase Workflow

**Agents:** 6 personas (5 analysts + 1 CIO)
**Mode:** Parallel (default)

### Phase 1: Rapid Analysis

Each analyst (100-150 words):
- Trend Architect: EMA stack, momentum
- Tape Reader: Volume profile, timing
- Mean-Reversion: RSI, exhaustion gaps
- Risk Manager: ATR stop, position size
- Sentiment & Flow: Fear/greed, options flow

### Phase 2: Parallel Challenge-Response

**Iteration Cap:** 3 rounds
**Confidence Threshold:** 90%

See [Parallel Challenge-Response Mode](#parallel-challenge-response-mode-new).

### Phase 3: Holistic Confidence Vote

Weighted voting with Bayesian confidence tracking.

### Phase 4: CIO Decision

**Conviction Levels:**
- High (5/5): All aligned, no concessions
- Medium (4/5): Minor disagreement
- Low (3/5): Weak consensus
- Avoid (<3/5): No edge

**Outputs:** Entry, target, stop (1-1.5x ATR), duration (7 days max), size (0.25-0.5%)

---

## Swing Trading Model (1w - 4w): 5-Phase Workflow

**Agents:** 10 personas (9 analysts + 1 CIO)
**Mode:** Parallel (default)

### Phase 1: Deep Analysis

Each analyst (150-200 words):

**Environment:**
1. Macro Strategist
2. Sentiment & Flow

**Directional:**
3. Trend Architect
4. Mean-Reversion Specialist
5. Fundamental Catalyst

**Evidence:**
6. Statistical Quant
7. Tape Reader

**Defense:**
8. Short-Seller
9. Risk Manager

### Phase 2: Parallel Challenge-Response

**Iteration Cap:** 5 rounds
**Confidence Threshold:** 90%

### Phase 3: Holistic Confidence Vote

Weighted voting with accuracy-based weights.

### Phase 4: CIO Synthesis

Count weighted votes, check contrarian edge, assess conviction.

---

## Position Trading Model (1m - 6m): 4-Phase Workflow

**Agents:** 7 personas
**Mode:** Parallel (default)

Same workflow as Swing with extended fundamental analysis.

---

## Investment Model (1y+): 4-Phase Workflow

**Agents:** 5 personas
**Mode:** Parallel (default)

Focus on fundamentals, moat analysis, secular trends.

---

## Monitoring Metrics

Track these metrics to ensure game-theoretic health:

| Metric | Description | Target Range |
|--------|-------------|--------------|
| Concession Rate | % challenges resulting in concession | 15-30% |
| Challenge Success Rate | % challenges that weakened target | 40-60% |
| Rounds to Convergence | Avg rounds before debate ends | 2-4 |
| Confidence at Convergence | Final Bayesian confidence | >85% |
| Persona Mute Rate | % debates with muted personas | <10% |
| Weighted Vote Accuracy | % weighted votes matching outcome | Track |

**Quality Indicators:**
- Concession rate <10%: Personas too stubborn
- Concession rate >40%: Challenges too weak
- Rounds always at max: Convergence failing
- Mute rate >20%: Threshold too aggressive

**View stats:**
```bash
python .claude/skills/trading-debate/scripts/persona_tracker.py --stats
```
