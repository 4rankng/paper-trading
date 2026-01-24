# Trading Debate Workflows Reference

Detailed execution workflows for each trading model.

---

## Iteration Limits (Efficiency Control)

| Model | Max Rounds | Early Stop Condition |
|-------|------------|---------------------|
| Scalping/Day | 3 rounds | All challenges addressed OR no new evidence |
| Swing | 5 rounds | Convergence pattern detected |
| Position | 5 rounds | Convergence pattern detected |
| Investment | 5 rounds | Convergence pattern detected |

**Early convergence**: If 2 consecutive rounds produce no new challenges, debate ends immediately.

---

## Shared Components

These components are common to all trading models and are referenced by model-specific workflows.

### Challenge-Response Debate Steps (All Models)

#### Step 2.1: Initial Challenges

Each persona X reviews all analyst answers and identifies:
- The answer they **disagree with most**
- The specific point(s) of disagreement

X then issues a **formal challenge** to that persona Y, stating:
1. What they disagree with (specific claim or conclusion)
2. Why they disagree (counter-evidence or logic)
3. What evidence would change their mind

#### Step 2.2: Response and Justification

The challenged persona Y must respond to X's challenge with:
1. **Justification**: Evidence or reasoning supporting their original position
2. **OR Concession**: If they cannot justify, they explicitly concede the point

A valid justification must include:
- Concrete data points from the analytics
- Logical reasoning that addresses the challenge
- Acknowledgment of any weaknesses in their position

#### Step 2.3: Iteration

The debate continues in rounds until:
- **No new challenges remain**, OR
- **Max rounds completed** (see [Iteration Limits](#iteration-limits-efficiency-control)), OR
- **2 consecutive rounds with no new challenges**

Any persona may issue new challenges based on responses. Once a persona concedes on a point, they retract that specific claim.

#### Step 2.4: Debate Convergence

The phase ends when:
- All outstanding challenges have been addressed
- All conceded points have been retracted
- Remaining disagreements are explicitly documented as "unresolved disputes"

### Shared Debate Rules

- **Must challenge**: Each persona must challenge at least one other answer
- **Must respond**: Challenged personas must always respond (justify or concede)
- **Specific challenges**: Challenges must be specific, not generic
- **Evidence-based**: All challenges and justifications must reference the analytics data
- **Good faith**: Personas concede when they cannot justify

### Phase 3: Holistic Confidence Vote (All Models)

After the challenge-response debate concludes, each analyst **holistically evaluates**:
- All original analyst answers
- All challenges issued
- All responses and justifications
- All conceded points
- Remaining unresolved disputes

**Scoring 1-10 based on the entire debate transcript:**
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Voting Guidance:**
- Vote for the **most well-defended** position, not necessarily your original stance
- Penalize positions that conceded key points
- Reward positions that successfully defended against challenges
- Consider the quality of evidence and reasoning, not just the conclusion
- **Contrarian Edge**: A lone dissent with strong evidence warrants "Watch" status, not automatic rejection

---

## Scalping/Day Trading Model (1d - 7d): 4-Phase Workflow

**Agents:** 6 personas (5 analysts + 1 CIO)

### Phase 1: Rapid Analysis

Each analyst persona (1-5) provides concise evaluation (100-150 words):

**Trend Architect:**
- Intraday trend structure (higher highs/lows or lower highs/lows)
- EMA alignment (20/50/200 stack)
- Momentum direction and sustainability

**Tape Reader:**
- Volume profile (accumulation/distribution/churn)
- Entry/exit timing (smart money detection)
- **Spread analysis** (liquidity check)
- Average daily volume >1M shares preferred

**Mean-Reversion Specialist:**
- Overbought/oversold conditions (RSI, Stochastics)
- Quick scalp opportunities (exhaustion gaps)
- Distance from mean (standard deviations)

**Risk Manager:**
- Stop distance based on ATR (1-1.5x)
- Position size calculation (0.25-0.5% max)
- Quick loss cut strategy
- **Liquidity check**: Minimum 20-day avg volume >500k shares

**Sentiment & Flow:**
- Intraday sentiment (fear/greed extremes)
- Options flow (calls/puts, gamma exposure)
- Hype detection (social volume spikes)

### Phase 2: Structured Challenge-Response Debate

**Iteration Cap: Maximum 3 rounds** (scalping requires speed)

See [Challenge-Response Debate Steps](#challenge-response-debate-steps-all-models) for detailed process.

**Debate Rules:** See [Shared Debate Rules](#shared-debate-rules).

### Phase 3: Holistic Confidence Vote

See [Phase 3: Holistic Confidence Vote](#phase-3-holistic-confidence-vote-all-models).

### Phase 4: CIO Decision

**Weighs 5 analyst inputs and debate outcomes, assesses conviction:**
- **High Conviction (5/5)**: All analysts aligned, no concessions
- **Medium Conviction (4/5)**: Minor disagreement, defended positions
- **Low Conviction (3/5)**: Weak consensus, some concessions
- **Avoid (<3/5)**: No edge

**Outputs day trading plan with:**
- Entry zone (often at market or limit near support)
- Target (quick profit, often 1-2% moves)
- Stop-loss (tight, 1-1.5x ATR)
- Duration: Same day to 7 days
- Time stop: Exit EOD if no movement
- Position size: 0.25-0.5%

**Liquidity Check (Scalping only):**
- Minimum average daily volume: 500k shares
- Maximum position size: <1% of daily volume
- Wide spreads (>2%) trigger reduction or skip

**Conviction Tiers:** See [constraints.md](constraints.md#scalpingday-trading-constraints-1d---7d).

---

## Swing Trading Model (1w - 4w): 5-Phase Workflow

**Agents:** 10 personas (9 analysts + 1 CIO)

### Phase 1: Deep Analysis

Each analyst persona (1-9) provides concise evaluation (150-200 words):

**Environment - Context Setting:**
1. Macro Strategist: Market regime, tailwinds/headwinds
2. Sentiment & Flow: Crowd positioning, contrarian signals

**Strategists - Directional Bias:**
3. Trend Architect: Trend structure, momentum alignment
4. Mean-Reversion Specialist: Overbought/oversold extremes
5. Fundamental Catalyst: Earnings, guidance, events

**Evidence - Validation:**
6. Statistical Quant: Z-scores, volatility, probability
7. Tape Reader: Volume confirmation, divergence detection

**Defense - Capital Preservation:**
8. Short-Seller: Red-teaming, structural flaws
9. Risk Manager: R:R, position sizing, correlation

### Phase 2: Structured Challenge-Response Debate

**Iteration Cap: Maximum 5 rounds**

See [Challenge-Response Debate Steps](#challenge-response-debate-steps-all-models) for detailed process.

**Debate Rules:** See [Shared Debate Rules](#shared-debate-rules).

### Phase 3: Holistic Confidence Vote

See [Phase 3: Holistic Confidence Vote](#phase-3-holistic-confidence-vote-all-models).

### Phase 4: CIO Synthesis

- Count votes from 9 analysts
- Identify consensus vs disagreement across personas
- Note any conceded points that weakened positions
- **Check for contrarian edge**: If 1-2 analysts dissent with strong evidence, flag for "Watch" rather than "Avoid"
- Assess conviction level and outputs trading plan

**Conviction Tiers:** See [constraints.md](constraints.md#swing-trading-constraints-1w---4w).

---

## Position Trading Model (1m - 6m): 4-Phase Workflow

**Agents:** 7 personas (6 analysts + 1 CIO)

### Phase 1: Analyst Deep Dive

Each analyst provides evaluation (200-250 words):

1. **Trend Architect** - Medium-term trend structure and sustainability
2. **Fundamental Catalyst** - Catalyst timeline and probability
3. **Sector Analyst** - Industry position, competitive moat
4. **Risk Manager** - Risk factors, position sizing
5. **Short-Seller** - Bear case, structural concerns
6. **Macro Strategist** - Macro environment, sector rotation

### Phase 2: Structured Challenge-Response Debate

**Iteration Cap: Maximum 5 rounds**

See [Challenge-Response Debate Steps](#challenge-response-debate-steps-all-models) for detailed process.

**Debate Rules:** See [Shared Debate Rules](#shared-debate-rules).

### Phase 3: Holistic Confidence Vote

See [Phase 3: Holistic Confidence Vote](#phase-3-holistic-confidence-vote-all-models).

### Phase 4: CIO Decision

- Weighs all analyst perspectives and debate outcomes
- Notes any conceded points that weakened positions
- Assesses conviction level (High/Medium/Low)
- Outputs position trading plan with entry zones, targets, and holding period

**Conviction Tiers:** See [constraints.md](constraints.md#position-trading-constraints-1m---6m).

---

## Investment Model (1y+): 4-Phase Workflow

**Agents:** 5 personas (4 analysts + 1 CIO)

### Phase 1: Fundamental Deep Dive

Each analyst provides comprehensive evaluation (250-300 words):

1. **Fundamental Analyst** - Business quality, moat, financial strength, valuation
2. **Growth Strategist** - Revenue trajectory, TAM, margin expansion
3. **Risk Manager** - Competitive threats, regulatory risks, business model
4. **Macro Strategist** - Secular tailwinds/headwinds, industry disruption

### Phase 2: Structured Challenge-Response Debate

**Iteration Cap: Maximum 5 rounds**

See [Challenge-Response Debate Steps](#challenge-response-debate-steps-all-models) for detailed process.

**Debate Rules:** See [Shared Debate Rules](#shared-debate-rules).

### Phase 3: Holistic Confidence Vote

See [Phase 3: Holistic Confidence Vote](#phase-3-holistic-confidence-vote-all-models).

### Phase 4: CIO Investment Decision

- Synthesizes fundamental view and debate outcomes
- Notes any conceded points that weakened positions
- Validates investment thesis
- Outputs investment recommendation with thesis, entry zone, and holding period

**Conviction Tiers:** See [constraints.md](constraints.md#investment-model-constraints-1y).

---

## Monitoring Metrics

Track these metrics across debates to identify biases and improve quality:

| Metric | Description | Target Range |
|--------|-------------|--------------|
| Concession Rate | % of challenges resulting in concession | 15-30% |
| Challenge Success Rate | % of challenges that weakened target position | 40-60% |
| Rounds to Convergence | Average rounds before debate ends | 2-4 |
| Unresolved Disputes | Average unresolved disputes per debate | 0-2 |
| Contrarian Edge Wins | % of lone dissents later proven correct | Track separately |

**Quality Indicators:**
- Concession rate <10%: Personas may be too stubborn
- Concession rate >40%: Challenges may be too weak
- Rounds always hitting max: Early convergence not working

**Track debates in:** `trading-debates/[TICKER]/` with metadata section for metrics
