# Debate Workflows Reference

Detailed execution workflows for each debate model.

---

## Iteration Limits (Efficiency Control)

| Model | Agents | Max Rounds | Early Stop Condition |
|-------|--------|------------|----------------------|
| Geopolitics | 6 analysts | 4 rounds | Convergence OR no new challenges |
| Economics | 8 analysts | 5 rounds | Convergence OR no new challenges |
| Policy | 7 analysts | 5 rounds | Convergence OR no new challenges |
| Markets | 5 analysts | 4 rounds | Convergence OR no new challenges |

**Early convergence**: If 2 consecutive rounds produce no new challenges, debate ends immediately.

---

# Geopolitics Model Workflow

**Agents:** 6 personas → Chief Analyst synthesis

## Phase 1: Topic Definition & Context Gathering

**Step 1.1: Define the Debate Question**

Ensure question is specific and debatable:
- Bad: "Will there be war?"
- Good: "What is the probability of military conflict between US and Iran escalating in the next 6 months?"

**Step 1.2: Gather Current Information**

Use tools to gather latest data:
- WebSearch for recent news on the topic
- WebReader for detailed analysis pieces
- Reddit for public sentiment (r/geopolitics, r/worldnews)
- Read existing macro files for context

**Step 1.3: Identify Key Facts**

Document undisputed facts as shared context:
- Current status of situation
- Key actors and their positions
- Timeline of recent events
- Economic/military data points

---

## Phase 2: Analyst Positions

Each persona provides their analysis (200-250 words):

**Diplomatic Historian:**
- Historical parallels and precedents
- What past situations suggest
- Red flags from history

**Regional Specialist:**
- Local context and dynamics
- Cultural factors at play
- Regional power structures

**Geoeconomic Strategist:**
- Economic interdependencies
- Sanctions/leverage options
- Economic pain tolerance

**Security Analyst:**
- Military balance assessment
- Escalation pathways
- Red lines and tripwires

**Game Theorist:**
- Strategic incentives
- Credibility assessment
- Rational actor analysis

**Public Opinion Analyst:**
- Domestic political constraints
- Public sentiment in key countries
- Coalition dynamics

---

## Phase 3: Structured Challenge-Response Debate

**Iteration Cap: Maximum 4 rounds**

**Step 3.1: Initial Challenges**

Each persona reviews all positions and identifies the answer they **disagree with most**, issuing a formal challenge:
1. What they disagree with (specific claim)
2. Why they disagree (counter-evidence)
3. What evidence would change their mind

**Step 3.2: Response and Justification**

Challenged persona responds with:
- **Justification**: Evidence supporting original position
- **OR Concession**: Explicit concession if cannot justify

**Step 3.3: Iteration**

Continue in rounds until:
- No new challenges remain, OR
- 4 rounds completed, OR
- 2 consecutive rounds with no new challenges

**Step 3.4: Document Convergence**

- Address all outstanding challenges
- Document "unresolved disputes"
- Note conceded positions

---

## Phase 4: Chief Analyst Synthesis

**Step 4.1: Evidence Assessment**

- Quality of sources (high/medium/low credibility)
- Recency of data
- Diversity of perspectives

**Step 4.2: Scenario Analysis**

Present probability-weighted scenarios:
- **Base Case** (most likely, 50-60%)
- **Bull Case** (positive outcome, 20-30%)
- **Bear Case** (negative outcome, 15-25%)

**Step 4.3: Confidence Assessment**

- **High (80%+)**: Strong consensus, robust evidence
- **Medium (60-80%)**: Clear direction with some uncertainty
- **Low (40-60%)**: Mixed signals, limited consensus
- **Research Needed (<40%)**: Insufficient information

**Step 4.4: Output Format**

```markdown
# Debate: [Topic]

**Date:** YYYY-MM-DD
**Model:** Geopolitics
**Confidence:** High/Medium/Low

## Executive Summary
[3-4 sentence summary]

## Points of Agreement
- [Key consensus points]

## Points of Disagreement
- [Key areas of debate]
- [Unresolved disputes]

## Scenarios

### Base Case (XX% probability)
[Description]

### Bull Case (XX% probability)
[Description]

### Bear Case (XX% probability)
[Description]

## Key Indicators to Monitor
- [Events/data to track]

## Sources
- [List sources with credibility assessment]
```

---

# Economics Model Workflow

**Agents:** 8 personas → Chief Analyst synthesis

## Phase 1: Data Gathering

**Gather latest economic data:**
- WebSearch for recent economic releases
- Read macro/theses/macro_thesis_YYYY_MM.md
- Check central bank calendar
- Review latest employment, inflation, GDP data

**Document Key Variables:**
- GDP growth rate
- Inflation (CPI, PCE)
- Unemployment rate
- Interest rates
- Consumer sentiment
- Business investment

---

## Phase 2: Analyst Positions

Each persona provides analysis (200-250 words):

**Economic Historian:**
- Historical parallels
- Cycle position assessment
- Policy precedent analysis

**Keynesian Economist:**
- Demand-side assessment
- Output gap analysis
- Stimulus/necessity evaluation

**Monetarist Economist:**
- Inflation risk assessment
- Monetary policy stance
- Money supply analysis

**Labor Market Analyst:**
- Employment trends
- Wage pressure analysis
- Participation factors

**International Economist:**
- Global linkages
- Trade/capital flows
- Exchange rate assessment

**Financial Stability Analyst:**
- Leverage/debt concerns
- Systemic risk indicators
- Bubble risk assessment

**Sector Analyst:**
- Industry-specific trends
- Supply chain health
- Innovation/disruption impacts

**Political Economist:**
- Policy feasibility
- Distributional effects
- Institutional constraints

---

## Phase 3: Structured Debate

**Same structure as Geopolitics model, max 5 rounds**

---

## Phase 4: Synthesis

**Economic Outlook Output:**

```markdown
# Economic Debate: [Topic]

**Date:** YYYY-MM-DD
**Model:** Economics
**Confidence:** High/Medium/Low

## Executive Summary
[3-4 sentence economic outlook]

## Economic Assessment

### Growth Outlook
[Bearish/Neutral/Bullish with reasoning]

### Inflation Outlook
[Disinflationary/Sticky/Accelerating with reasoning]

### Policy Implications
[Recommended policy stance]

## Sector Implications
| Sector | Outlook | Key Drivers |
|--------|---------|-------------|
| [Sector] | [Tailwind/Headwind] | [Drivers] |

## Risks to Outlook
- [Key downside risks]
- [Key upside risks]

## Data to Monitor
- [Key releases to watch]

## Sources
```

---

# Policy Model Workflow

**Agents:** 7 personas → Chief Analyst synthesis

## Phase 1: Policy Context

**Gather policy information:**
- WebSearch for latest policy news
- Read bill text or policy proposals
- Analyze stakeholder positions
- Review polling data

**Document Policy Framework:**
- Proposed policy content
- Proponents/opponents
- Timeline/path to enactment
- Implementation requirements

---

## Phase 2: Analyst Positions

Each persona (200-250 words):

**Policy Historian:**
- Historical precedents
- Past implementation attempts
- Lessons learned

**Public Finance Economist:**
- Fiscal impact
- Cost-benefit analysis
- Distributional effects

**Regulatory Analyst:**
- Market impact
- Unintended consequences
- Incentive structures

**Implementation Specialist:**
- Administrative capacity
- Timeline feasibility
- Execution challenges

**Legal Analyst:**
- Constitutionality
- Legal challenges
- Regulatory authority

**Public Opinion Specialist:**
- Public support levels
- Messaging assessment
- Coalition potential

**Stakeholder Analyst:**
- Interest group positions
- Veto player analysis
- Compensation strategies

---

## Phase 3: Structured Debate

**Max 5 rounds**

---

## Phase 4: Synthesis

```markdown
# Policy Debate: [Policy]

**Date:** YYYY-MM-DD
**Model:** Policy
**Confidence:** High/Medium/Low

## Executive Summary
[3-4 sentence policy assessment]

## Policy Analysis

### Likely Impact
[What happens if enacted]

### Feasibility Assessment
| Factor | Assessment |
|--------|------------|
| Political Feasibility | [High/Medium/Low] |
| Implementation Capacity | [High/Medium/Low] |
| Legal Risk | [High/Medium/Low] |
| Public Support | [High/Medium/Low] |

### Unintended Consequences
- [Potential negative side effects]

## Stakeholder Analysis
| Group | Position | Influence |
|-------|----------|-----------|
| [Group] | [Support/Oppose] | [High/Med/Low] |

## Recommendation
[Pass/Modify/Reject with reasoning]

## Key Milestones
- [Dates to watch]
```

---

# Markets Model Workflow

**Agents:** 5 personas → Chief Market Strategist synthesis

## Phase 1: Market Context

**Gather market data:**
- Read macro/theses/macro_thesis_YYYY_MM.md
- WebSearch for latest market commentary
- Review sector performance
- Check latest economic releases

---

## Phase 2: Analyst Positions

Each persona (200-250 words):

**Macro Strategist:**
- Economic regime assessment
- Growth/inflation outlook
- Sector implications

**Cross-Asset Strategist:**
- Asset class relationships
- Relative value opportunities
- Risk-on/off assessment

**Market Historian:**
- Historical parallels
- Valuation comparisons
- Cycle position

**Sentiment Analyst:**
- Positioning extremes
- Crowded trades
- Contrarian signals

---

## Phase 3: Structured Debate

**Max 4 rounds**

---

## Phase 4: Synthesis

```markdown
# Market Debate: [Topic]

**Date:** YYYY-MM-DD
**Model:** Markets
**Confidence:** High/Medium/Low

## Executive Summary
[3-4 sentence market outlook]

## Market Regime Assessment

### Current Regime
[Risk-On / Risk-Off / Transition]

### Key Drivers
- [Primary market drivers]

## Asset Class Views

| Asset | View (3M) | View (12M) | Rationale |
|-------|-----------|------------|-----------|
| Equities | [Bull/Neutral/Bear] | [Bull/Neutral/Bear] | [Why] |
| Bonds | [Bull/Neutral/Bear] | [Bull/Neutral/Bear] | [Why] |
| Commodities | [Bull/Neutral/Bear] | [Bull/Neutral/Bear] | [Why] |
| USD | [Bull/Neutral/Bear] | [Bull/Neutral/Bear] | [Why] |

## Sector Views

| Sector | Rating | Key Drivers |
|--------|--------|-------------|
| [Sector] | [Overweight/Equal/Underweight] | [Drivers] |

## Key Risks
- [Primary risks to outlook]

## Tactical Recommendations
- [Specific actionable views]
```

---

# Quality Standards

## Debate Quality Indicators

| Metric | Target Range |
|--------|--------------|
| Concession Rate | 15-30% |
| Challenge Success Rate | 40-60% |
| Rounds to Convergence | 2-4 |
| Unresolved Disputes | 0-3 |
| Source Diversity | 5+ sources minimum |

## Source Credibility Standards

| Tier | Sources |
|------|---------|
| High | Central banks, government agencies, major news wires, academic papers |
| Medium | Think tanks, industry publications, established commentators |
| Low | Social media, anonymous sources, partisan outlets |

## Red Flags to Avoid

- **Anchoring bias**: Overweighting first information
- **Confirmation bias**: Seeking only supporting evidence
- **Recency bias**: Overweighting latest data
- **Authority bias**: Deferring to "experts" without scrutiny
- **This time is different**: Ignoring historical precedents

## When to Declare "Insufficient Data"

- <3 credible sources on topic
- Major events pending (Fed decision, election)
- Data stale (>7 days old for fast-moving topics)
- Conflicting sources with no resolution path

**Output:** "Research Needed - Insufficient reliable data to form conclusion. Recommend gathering [specific missing information]."
