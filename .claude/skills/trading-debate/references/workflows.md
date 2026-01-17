# Trading Debate Workflows Reference

Detailed execution workflows for each trading model.

---

## Scalping/Day Trading Model (1d - 7d): 3-Phase Workflow

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
- Spread analysis (wide/narrow)

**Mean-Reversion Specialist:**
- Overbought/oversold conditions (RSI, Stochastics)
- Quick scalp opportunities (exhaustion gaps)
- Distance from mean (standard deviations)

**Risk Manager:**
- Stop distance based on ATR (1-1.5x)
- Position size calculation (0.25-0.5% max)
- Quick loss cut strategy

**Sentiment & Flow:**
- Intraday sentiment (fear/greed extremes)
- Options flow (calls/puts, gamma exposure)
- Hype detection (social volume spikes)

### Phase 2: Quick Risk Check

**Risk Manager validates:**
- R:R >= 2:1 (lowered for day trades)
- Tight stop distance (1-1.5x ATR)
- Position size >= 0.25%

**Tape Reader confirms:**
- Volume available for entry/exit
- Liquidity sufficient (not trading during pre/post market only)

### Phase 3: CIO Decision

**Weighs 5 analyst inputs and assesses conviction:**
- **High Conviction (5/5)**: All analysts aligned
- **Medium Conviction (4/5)**: Minor disagreement
- **Low Conviction (3/5)**: Weak consensus
- **Avoid (<3/5)**: No edge

**Outputs day trading plan with:**
- Entry zone (often at market or limit near support)
- Target (quick profit, often 1-2% moves)
- Stop-loss (tight, 1-1.5x ATR)
- Duration: Same day to 7 days
- Time stop: Exit EOD if no movement
- Position size: 0.25-0.5%

**Veto Triggers (Non-negotiable):**
- Risk Manager: R:R < 2:1, position <0.25%, correlation >60%

---

## Swing Trading Model (1w - 4w): 4-Phase Workflow

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

### Phase 2: Adversarial Debate

- **Short-Seller** red-teams the bullish thesis with structural flaws
- **Risk Manager** challenges R:R and position sizing
- **Tape Reader** validates volume confirmation
- **Sentiment & Flow** provides contrarian perspective

### Phase 3: Confidence Vote

Each analyst scores 1-10:
- 1-3 = Avoid
- 4-6 = Neutral/Watch
- 7-8 = Buy (Speculative)
- 9-10 = Strong Buy (High Conviction)

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
- Apply conviction thresholds:
  - **8-9/9 bullish** → High Conviction (full position 0.25-1%)
  - **6-7/9 bullish** → Speculative Conviction (reduced 0.25-0.5%)
  - **5/9 bullish** → Watch/Neutral (Low Conviction)
  - **<5/9 bullish** → Avoid

---

## Position Trading Model (1m - 6m): 3-Phase Workflow

**Agents:** 7 personas (6 analysts + 1 CIO)

### Phase 1: Analyst Deep Dive

Each analyst provides evaluation (200-250 words):

1. **Trend Architect** - Medium-term trend structure and sustainability
2. **Fundamental Catalyst** - Catalyst timeline and probability
3. **Sector Analyst** - Industry position, competitive moat
4. **Risk Manager** - Risk factors, position sizing
5. **Short-Seller** - Bear case, structural concerns
6. **Macro Strategist** - Macro environment, sector rotation

### Phase 2: Synthesis Debate

Analysts discuss and challenge views, focusing on:
- Catalyst conviction and timeline
- Trend structure validation
- Risk/reward assessment

### Phase 3: CIO Decision

- Weighs all analyst perspectives
- Assesses conviction level (High/Medium/Low)
- Outputs position trading plan with entry zones, targets, and holding period

**Conviction Tiers:**
- **High Conviction (5-6/6)**: Full position (0.5-2%)
- **Medium Conviction (4/6)**: Reduced position (0.5-1%)
- **Avoid (<4/6)**: No trade

---

## Investment Model (1y+): 3-Phase Workflow

**Agents:** 5 personas (4 analysts + 1 CIO)

### Phase 1: Fundamental Deep Dive

Each analyst provides comprehensive evaluation (250-300 words):

1. **Fundamental Analyst** - Business quality, moat, financial strength, valuation
2. **Growth Strategist** - Revenue trajectory, TAM, margin expansion
3. **Risk Manager** - Competitive threats, regulatory risks, business model
4. **Macro Strategist** - Secular tailwinds/headwinds, industry disruption

### Phase 2: Thesis Validation

Analysts debate and stress-test the investment thesis:
- Moat durability
- Growth sustainability
- Valuation justification
- Long-term risk scenarios

### Phase 3: CIO Investment Decision

- Synthesizes fundamental view
- Validates investment thesis
- Outputs investment recommendation with thesis, entry zone, and holding period

**Conviction Tiers:**
- **High Conviction (4/4)**: Full position (1-5%)
- **Medium Conviction (3/4)**: Reduced position (1-3%)
- **Avoid (<3/4)**: No investment
