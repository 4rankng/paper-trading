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

**Step 2.1: Initial Challenges**

Each persona X reviews all 5 analyst answers and identifies the answer they **disagree with most**, issuing a formal challenge stating:
1. What they disagree with (specific claim or conclusion)
2. Why they disagree (counter-evidence or logic)
3. What evidence would change their mind

**Step 2.2: Response and Justification**

The challenged persona Y must respond with:
- **Justification**: Evidence or reasoning supporting their original position
- **OR Concession**: Explicit concession if they cannot justify

**Step 2.3: Iteration (max 3 rounds)**

The debate continues in rounds until:
- **No new challenges remain**, OR
- **3 rounds completed**, OR
- **2 consecutive rounds with no new challenges**

**Step 2.4: Debate Convergence**

The phase ends when all outstanding challenges are addressed and remaining disagreements are documented as "unresolved disputes."

**Debate Rules:**
- **Must challenge**: Each persona must challenge at least one other answer
- **Must respond**: Challenged personas must always respond (justify or concede)
- **Specific challenges**: Challenges must be specific, not generic
- **Evidence-based**: All challenges and justifications must reference the analytics data
- **Good faith**: Personas concede when they cannot justify

### Phase 3: Holistic Confidence Vote

After the challenge-response debate, each analyst **holistically evaluates** the entire debate transcript and scores 1-10:
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Voting Guidance:**
- Vote for the **most well-defended** position, not necessarily your original stance
- Penalize positions that conceded key points
- Reward positions that successfully defended against challenges

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

**Veto Triggers (Non-negotiable):**
- Risk Manager: R:R < 2:1, position <0.25%, correlation >60%
- Liquidity: Daily volume <500k shares OR spread >2%

---

## Swing Trading Model (1w - 4w): 5-Phase Workflow

**Agents:** 10 personas (9 analysts + 1 CIO) in 4 clusters

### Phase 1: Deep Analysis

Each analyst persona (1-9) provides concise evaluation (150-200 words) based on their cluster lens:

**Cluster 1 - Environment:**
1. Macro Strategist: Market regime, tailwinds/headwinds
2. Sentiment & Flow: Crowd positioning, contrarian signals

**Cluster 2 - Strategists:**
3. Trend Architect: Trend structure, momentum alignment
4. Mean-Reversion Specialist: Overbought/oversold extremes
5. Fundamental Catalyst: Earnings, guidance, events

**Cluster 3 - Evidence:**
6. Statistical Quant: Z-scores, volatility, probability
7. Tape Reader: Volume confirmation, divergence detection

**Cluster 4 - Defense:**
8. Short-Seller: Red-teaming, structural flaws
9. Risk Manager: R:R, position sizing, correlation

### Phase 2: Structured Challenge-Response Debate

**Iteration Cap: Maximum 5 rounds**

**Step 2.1: Initial Challenges**

Each persona X reviews all 9 analyst answers and identifies:
- The answer they **disagree with most**
- The specific point(s) of disagreement

X then issues a **formal challenge** to that persona Y, stating:
1. What they disagree with (specific claim or conclusion)
2. Why they disagree (counter-evidence or logic)
3. What evidence would change their mind

**Step 2.2: Response and Justification**

The challenged persona Y must respond to X's challenge with:
1. **Justification**: Evidence or reasoning supporting their original position
2. **OR Concession**: If they cannot justify, they explicitly concede the point

A valid justification must include:
- Concrete data points from the analytics
- Logical reasoning that addresses the challenge
- Acknowledgment of any weaknesses in their position

**Step 2.3: Iteration (max 5 rounds)**

The debate continues in rounds:
1. Any persona may issue new challenges based on responses
2. Challenged personas must respond or concede
3. Once a persona concedes on a point, they retract that specific claim
4. The process continues until:
   - **No new challenges remain**, OR
   - **5 rounds completed**, OR
   - **2 consecutive rounds with no new challenges**

**Step 2.4: Debate Convergence**

The phase ends when:
- All outstanding challenges have been addressed
- All conceded points have been retracted
- Remaining disagreements are explicitly documented as "unresolved disputes"

**Debate Rules:**
- **Must challenge**: Each persona must challenge at least one other answer
- **Must respond**: Challenged personas must always respond (justify or concede)
- **Specific challenges**: Challenges must be specific, not generic
- **Evidence-based**: All challenges and justifications must reference the analytics data
- **Good faith**: Personas concede when they cannot justify

### Phase 3: Holistic Confidence Vote

After the challenge-response debate concludes, each analyst **holistically evaluates**:
- All original analyst answers
- All challenges issued
- All responses and justifications
- All conceded points
- Remaining unresolved disputes

Each analyst scores 1-10 based on the **entire debate transcript**, not just their original view:
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Voting Guidance:**
- Vote for the **most well-defended** position, not necessarily your original stance
- Penalize positions that conceded key points
- Reward positions that successfully defended against challenges
- Consider the quality of evidence and reasoning, not just the conclusion
- **Contrarian Edge**: A lone dissent (1/9) with strong evidence warrants "Watch" status, not automatic rejection

### Phase 4: CIO Synthesis (with Veto Check)

**Step 1: Check Vetoes (Non-negotiable, happens FIRST)**

**Risk Manager Veto (Line-Item - Absolute):**
- R:R < 3:1? → AUTO-VETO
- Position < 0.25%? → AUTO-VETO
- Correlation > 60%? → AUTO-VETO

**Macro Strategist Veto (Contextual):**
- SPY below MA-200 AND VIX > 30? → AUTO-VETO longs
- Major event imminent (Fed, CPI)? → CAP at Low Conviction

**If veto triggered** → Output "AVOID - Veto triggered" and STOP analysis

**Step 2: Synthesize (only if no veto)**

- Count votes from 9 analysts
- Identify consensus vs disagreement across clusters
- Note any conceded points that weakened positions
- **Check for contrarian edge**: If 1-2 analysts dissent with strong evidence, flag for "Watch" rather than "Avoid"
- Apply conviction thresholds:
  - **8-9/9 bullish** → High Conviction (full position 0.25-1%)
  - **6-7/9 bullish** → Speculative Conviction (reduced 0.25-0.5%)
  - **5/9 bullish** → Watch/Neutral (Low Conviction)
  - **<5/9 bullish** → Avoid

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

**Step 2.1: Initial Challenges**

Each persona X reviews all 6 analyst answers and identifies the answer they **disagree with most**, issuing a formal challenge stating:
1. What they disagree with (specific claim or conclusion)
2. Why they disagree (counter-evidence or logic)
3. What evidence would change their mind

**Step 2.2: Response and Justification**

The challenged persona Y must respond with:
- **Justification**: Evidence or reasoning supporting their original position
- **OR Concession**: Explicit concession if they cannot justify

**Step 2.3: Iteration (max 5 rounds)**

The debate continues in rounds until:
- **No new challenges remain**, OR
- **5 rounds completed**, OR
- **2 consecutive rounds with no new challenges**

**Step 2.4: Debate Convergence**

The phase ends when all outstanding challenges are addressed and remaining disagreements are documented as "unresolved disputes."

**Debate Rules:**
- **Must challenge**: Each persona must challenge at least one other answer
- **Must respond**: Challenged personas must always respond (justify or concede)
- **Specific challenges**: Challenges must be specific, not generic
- **Evidence-based**: All challenges and justifications must reference the analytics data
- **Good faith**: Personas concede when they cannot justify

### Phase 3: Holistic Confidence Vote

After the challenge-response debate, each analyst **holistically evaluates** the entire debate transcript (original answers, challenges, responses, concessions, unresolved disputes) and scores 1-10:
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Voting Guidance:**
- Vote for the **most well-defended** position, not necessarily your original stance
- Penalize positions that conceded key points
- Reward positions that successfully defended against challenges
- Consider the quality of evidence and reasoning
- **Contrarian Edge**: A lone dissent (1/6) with strong evidence warrants consideration

### Phase 4: CIO Decision

- Weighs all analyst perspectives and debate outcomes
- Notes any conceded points that weakened positions
- Assesses conviction level (High/Medium/Low)
- Outputs position trading plan with entry zones, targets, and holding period

**Conviction Tiers:**
- **High Conviction (5-6/6)**: Full position (0.5-2%)
- **Medium Conviction (4/6)**: Reduced position (0.5-1%)
- **Avoid (<4/6)**: No trade

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

**Step 2.1: Initial Challenges**

Each persona X reviews all 4 analyst answers and identifies the answer they **disagree with most**, issuing a formal challenge stating:
1. What they disagree with (specific claim or conclusion)
2. Why they disagree (counter-evidence or logic)
3. What evidence would change their mind

**Step 2.2: Response and Justification**

The challenged persona Y must respond with:
- **Justification**: Evidence or reasoning supporting their original position
- **OR Concession**: Explicit concession if they cannot justify

**Step 2.3: Iteration (max 5 rounds)**

The debate continues in rounds until:
- **No new challenges remain**, OR
- **5 rounds completed**, OR
- **2 consecutive rounds with no new challenges**

**Step 2.4: Debate Convergence**

The phase ends when all outstanding challenges are addressed and remaining disagreements are documented as "unresolved disputes."

**Debate Rules:**
- **Must challenge**: Each persona must challenge at least one other answer
- **Must respond**: Challenged personas must always respond (justify or concede)
- **Specific challenges**: Challenges must be specific, not generic
- **Evidence-based**: All challenges and justifications must reference the analytics data
- **Good faith**: Personas concede when they cannot justify

### Phase 3: Holistic Confidence Vote

After the challenge-response debate, each analyst **holistically evaluates** the entire debate transcript (original answers, challenges, responses, concessions, unresolved disputes) and scores 1-10:
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

**Voting Guidance:**
- Vote for the **most well-defended** position, not necessarily your original stance
- Penalize positions that conceded key points
- Reward positions that successfully defended against challenges
- Consider the quality of evidence and reasoning

### Phase 4: CIO Investment Decision

- Synthesizes fundamental view and debate outcomes
- Notes any conceded points that weakened positions
- Validates investment thesis
- Outputs investment recommendation with thesis, entry zone, and holding period

**Conviction Tiers:**
- **High Conviction (4/4)**: Full position (1-5%)
- **Medium Conviction (3/4)**: Reduced position (1-3%)
- **Avoid (<3/4)**: No investment

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
| Veto Trigger Rate | % of debates stopped by veto | 10-20% |

**Quality Indicators:**
- Concession rate <10%: Personas may be too stubborn
- Concession rate >40%: Challenges may be too weak
- Rounds always hitting max: Early convergence not working
- Veto rate <5%: Risk Manager not engaged enough

**Track debates in:** `trading-debates/[TICKER]/` with metadata section for metrics
