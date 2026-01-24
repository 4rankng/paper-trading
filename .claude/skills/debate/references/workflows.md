# Truth-Seeking Debate Workflow

Multi-agent adversarial reasoning designed to converge on truth through elimination of falsified positions.

---

## Quick Reference: Persona Selection by Topic

| Topic Type | Persona Numbers |
|------------|----------------|
| Geopolitics | 1, 2, 3, 4, 12 |
| Monetary Policy | 5, 7, 10, 12 |
| Fiscal/Trade Policy | 5, 6, 8, 13 |
| Climate/Energy | 4, 6, 9, 12 |
| Emerging Markets | 6, 10, 11, 3 |
| Financial Crisis | 5, 10, 7, 12 |
| Technology Policy | 4, 8, 9, 13 |
| Education Policy | 5, 6, 14, 13, 7 |
| Healthcare Policy | 5, 6, 14, 13, 9 |
| Urban/Housing Policy | 6, 10, 15, 13, 3 |
| Social/Cultural Issues | 14, 16, 17, 12, 6 |
| Technology & Society | 4, 18, 16, 17, 13 |

**Persona key:** 1=Realist IR, 2=Regional Security, 3=Geoeconomic, 4=Tech & Econ Power, 5=Central Banker, 6=Development Economist, 7=Labor Market, 8=Trade Policy, 9=Climate-Economy, 10=Financial Stability, 11=EM Investor, 12=Historian, 13=Policy Implementation, 14=Public Policy, 15=Urban Development, 16=Sociologist, 17=Legal Scholar, 18=Tech Ethics

---

## Truth-Seeking Workflow (8 Steps)

### Step 1: Define a Falsifiable Question

The question determines the quality of the debate.

**Question Requirements:**

| Requirement | Example | Non-Example |
|-------------|---------|-------------|
| Falsifiable | "Will Fed cut rates by 25bp in January?" | "What should the Fed do?" |
| Time-bounded | "in Q1 2026" | "eventually" |
| Outcome-focused | "What is the probability of X?" | "Is X good or bad?" |
| Specific | "Will tariff levels exceed 25%?" | "Will trade war continue?" |

**Quality Gate:** Can you specify what evidence would prove each possible answer wrong? If no, reframe.

---

### Step 2: Select Adversarial Personas

See `quality-gates.md` for the Enhanced Persona Selection Matrix.

**Selection Criteria:**
- 5-7 personas with 3+ different analytical frameworks
- Always include Historian (12) OR Policy Implementation (13) for grounding
- Ensure genuine adversarial diversity (at least 2 with opposing priors)
- Each persona must have domain expertise relevant to the causal mechanisms

**Conflict Validation:**
1. Who will disagree with whom and on what?
2. Are there genuine cruxes of disagreement?
3. Can available evidence resolve these disputes?

---

### Step 3: Gather Evidence (Shared Context)

**3-Round Parallel Search:**

#### Round 1: Baseline Facts
```bash
mcp__web-search-prime__webSearchPrime("[topic] latest developments")
mcp__web-search-prime__webSearchPrime("[topic] historical precedents")
mcp__web-search-prime__webSearchPrime("[topic] expert consensus")
```

#### Round 2: Depth & Contrarian Views
```bash
mcp__web-search-prime__webSearchPrime("[topic] quantitative data metrics")
mcp__web-search-prime__webSearchPrime("[topic] official statements policy")
mcp__web-search-prime__webSearchPrime("[topic] contrarian views critique")
```

#### Round 3: Validation
- Cross-reference key claims
- Assess source credibility
- Identify data gaps

**Output: Shared Context Document**
```markdown
## Shared Context Document

### Established Facts
- [Claim] - Sources: [A, B] - Confidence: High/Medium/Low

### Disputed Claims
- [Claim A] - Source X argues Y
- [Counter-claim B] - Source Z argues W

### Data Gaps
- [Missing information that would resolve key questions]
```

---

### Step 4: Generate Initial Positions

Each persona presents a position focused on **causal mechanism** and **falsifiability**.

**See `constraints.md` for the complete Position Structure template.**

**Key requirements:**
- Core Thesis with probability
- Causal Mechanism (WHY this will happen)
- Key Evidence (3+ datapoints)
- Conditional Logic (IF/THEN statements)
- Acknowledged Weaknesses
- Falsification Criteria (what would prove this wrong)

**Quality Gate:** Every position must have falsification criteria. Positions without are invalid.

---

### Step 5: Adversarial Challenge Rounds

**Goal:** Eliminate false positions through systematic critique.

#### Round 1: Foundational Challenges

Each persona challenges the **weakest causal link** in another position.

**See `constraints.md` for complete Challenge Format and Response Options.**

**Summary:**
- **Challenge Type:** [Causal / Empirical / Logical]
- **The Flaw:** Specific weakness in causal mechanism or evidence
- **Counter-Evidence:** Data that contradicts
- **Response Options:** Full Defense / Partial Concession / Full Concession

#### Rounds 2+: Adaptive Challenges

- Target the weakest-defended positions
- Build on previous concessions
- Introduce new evidence if available

**Target Concession Rate:** 15-30% of challenges result in concessions.

Below 15% suggests groupthink or insufficient rigor. Above 30% suggests weak initial positions.

#### Stop Conditions

**See `quality-gates.md` for Stop Conditions.**

Summary: Debate stops at 80% convergence, plateau, crux-identified disagreements, or 5 rounds.

---

### Step 6: Track Convergence

**See `quality-gates.md` for the complete Convergence Map template.**

After each round, document:
- Positions Eliminated (Falsified)
- Positions Strengthened (Withstood Challenges)
- Emerging Consensus
- Persistent Disagreements (Cruxes)
- Convergence Score

**Convergence = Truth Signal**

| Convergence | Interpretation |
|-------------|----------------|
| 80%+ | High confidence - surviving position likely true |
| 60-80% | Medium confidence - direction clear, uncertainty remains |
| 40-60% | Low confidence - multiple viable scenarios |
| <40% | Insufficient evidence - research needed |

---

### Step 7: Synthesize Prediction

See `synthesis-format.md` for the complete output template.

**Required Output:**
1. **Executive Summary** - Prediction with probability and key reasoning
2. **Analysis Quality Metrics** - Source credibility, perspective diversity, convergence
3. **Consensus Findings** - What personas agree/disagree on
4. **Causal Mechanism** - Why the predicted outcome will occur
5. **Critical Uncertainties** - What could change the prediction
6. **Scenario Analysis** - Alternative outcomes with triggers
7. **Monitoring Framework** - Leading indicators to track
8. **Confidence Assessment** - Probability with justification

---

### Step 8: Calibrate

After outcomes are known, return and assess:

```markdown
## Prediction Calibration

**Original Prediction:** [What we said would happen]
**Actual Outcome:** [What actually happened]
**Calibration:** [Was our confidence appropriate?]

**Learning:**
- Which analytical frameworks proved most accurate?
- Which evidence was most predictive?
- What did we miss?
```

**Track calibration over time** to improve prediction quality.

---

## Requirements Summary

| Requirement | Specification | Source |
|-------------|---------------|--------|
| Minimum sources | 5+ credible sources | `quality-gates.md` |
| Concession rate | 15-30% of challenges | `constraints.md` |
| Target convergence | 60-80% for usable prediction | `quality-gates.md` |
| Source credibility | High/Medium tier only | `constraints.md` |
| Falsifiability | Every position must specify | `constraints.md` |
| Position structure | Causal mechanism + evidence | `constraints.md` |
| Output format | Prediction template | `synthesis-format.md` |
