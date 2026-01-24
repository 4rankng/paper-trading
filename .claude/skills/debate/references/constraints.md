# Debate Constraints Reference

Truth-seeking standards, position structure, and adversarial challenge protocols.

---

## 1. Factual Accuracy Requirements

### Source Standards

**All claims must be sourced from:**
- Government agencies (Fed, BLS, BEA, etc.)
- Central banks (Fed, ECB, BOJ, etc.)
- Major news organizations (Reuters, Bloomberg, WSJ, FT, etc.)
- International organizations (IMF, World Bank, UN, etc.)
- Academic research or established think tanks

**Unacceptable sources:**
- Social media rumors
- Anonymous sources
- Partisan outlets without corroboration
- Predictions without methodology

### Source Citation Format

```markdown
According to [Source], [Data Point] as of [Date].
Source: [URL or citation]
```

**Example:**
> According to the BLS, unemployment was 4.1% in December 2025. Source: BLS.gov

### Hierarchy of Evidence Credibility

```
1. Official data (primary source, verified)
2. Peer-reviewed research with methodology
3. Established expert consensus
4. Reputable news with named sources
5. Analysis with transparent methodology
6. Expert opinion with reasoning
7. Speculation with caveats
```

### Evidence Weighting Guidelines

| Evidence Type | Weight | Example |
|---------------|--------|---------|
| Official statistics | 1.0 | Fed data, BLS reports |
| Academic research | 0.9 | Peer-reviewed studies |
| Central bank communications | 0.9 | FOMC minutes, speeches |
| Government policy documents | 0.85 | Legislation, white papers |
| Major financial journalism | 0.7 | Reuters, Bloomberg, FT |
| Think tank analysis | 0.6 | Brookings, Cato (varies by bias) |
| Expert commentary | 0.5 | Op-eds, interviews |

### Conflicting Evidence Resolution

When sources conflict:
1. Check recency - More recent data preferred
2. Check methodology - Primary sources > secondary reporting
3. Check bias - Independent sources > partisan
4. Check consensus - Multiple sources > single source
5. Document uncertainty - Note when resolution isn't possible

---

## 2. Position Structure for Truth-Seeking

Every persona position MUST include:

```markdown
**[Persona Role]**

**Core Thesis:** [Single-sentence prediction with probability if applicable]

**Causal Mechanism:** [Which lens/theory informs this view?]

**Key Evidence:**
1. [Most important datapoint/precedent]
2. [Supporting evidence]
3. [Supporting evidence]

**Conditional Logic:**
- IF [condition], THEN [outcome shifts to...]
- Confidence increases/decreases if [indicator moves]

**Acknowledged Uncertainties:**
- [What could I be wrong about?]
- [Which assumptions are weakest?]

**Falsification Criteria:** [What evidence would change this position?]
```

### Causal Mechanism Requirement

Every position must explain **WHY** the predicted outcome will occur, not just **WHAT** will occur.

**Causal Chain Structure:**
1. Starting Condition → Current state or context
2. Action/Event → What will happen
3. Intermediate Effects → Chain of consequences
4. Final Outcome → Predicted result

### Falsifiability Standards

**Every position must include falsification criteria.**

| Position Type | Good Falsification Criteria | Bad (Unfalsifiable) |
|---------------|----------------------------|---------------------|
| Policy prediction | "Policy fails if unemployment >X% after Y months" | "Policy may face headwinds" |
| Economic forecast | "Recession occurs if 2 consecutive quarters GDP contraction" | "Economic uncertainty remains elevated" |
| Geopolitical | "Conflict escalates if troop levels exceed X at border Y" | "Tensions remain concerning" |

### Unfalsifiable Claims (Avoid)

- "Markets are uncertain about X"
- "There are risks on both sides"
- "Time will tell"
- "It depends on various factors"

**Quality Gate:** If a position lacks falsification criteria, it must be revised before debate proceeds.

---

## 3. Challenge-Response System

### Challenge Requirements

**Every persona MUST:**
1. Challenge at least one other persona's position per round
2. Target the **causal mechanism** or **evidence**
3. Provide counter-evidence or reasoning
4. Specify what would change their mind

### Challenge Format

```markdown
**[Challenger] challenges [Target] on [specific claim]:**

**Type:** [Causal / Empirical / Logical]

**The Flaw:** [Specific weakness in the causal mechanism or evidence]

**Counter-Evidence:** [Data or precedent that contradicts]

**Question for Target:** [What would you need to show to defend this claim?]
```

### Invalid Challenges

- Vague disagreements ("I think you're wrong")
- Personal attacks
- Challenges without evidence
- Moving goalposts
- Straw man arguments

### Response Options

```markdown
**[Target] responds:**

**Response Type:** [Full Defense / Partial Concession / Full Concession]

**If Defense:**
- **Counter-evidence:** [Data supporting original position]
- **Rebuttal:** [Why challenger's evidence doesn't undermine core causal claim]
- **Refined position:** [Clarification if needed, not retreat]

**If Partial Concession:**
- **Acknowledged flaw:** [Specific aspect that was incorrect]
- **Retained core:** [What remains valid and why]
- **Updated probability/confidence:** [New assessment]

**If Full Concession:**
- **What changed:** [Why original position untenable]
- **New position:** [Updated view based on challenge]
```

### Concession Rules

**When to concede:**
- Cannot provide supporting evidence
- Counter-evidence is stronger
- Original claim was based on incorrect data
- Realized logical flaw in causal mechanism

**Concession format:**
```markdown
**CONCESSION:** I acknowledge [specific point] is incorrect/weak.
**RETRACTION:** I retract my claim about [specific claim].
**REVISED POSITION:** [New position based on better understanding]
```

**NOT a concession:**
- "I see your point but..." (deflection)
- "That's one way to look at it" (evasion)
- Changing the subject
- Moving goalposts

### Target Concession Rate

**15-30% of challenges should result in concessions.**

- Below 15%: Positions may be too rigid, challenges too weak, or groupthink present
- Above 30%: May indicate weak initial positions or excessive concessions

---

## 4. Round Structure

### Round 1 - Foundational Challenges

Each persona:
- Identifies their strongest disagreement with another position
- Focuses on core assumptions, causal mechanisms, or evidence interpretation
- Must cite specific evidence or logical flaw

### Round 2+ - Adaptive Challenges

Personas:
- Target weakest-defended positions or unaddressed counterarguments
- Build on previous concessions
- Introduce new evidence if available

### Stop Conditions

**See `quality-gates.md` for complete Stop Conditions list.**

Summary: Debate stops when convergence >80%, plateau reached, disagreements are crux-identified, or 5 rounds complete.

---

## 5. Confidence Thresholds

### High Confidence (80%+)

**Required:**
- Strong consensus across personas
- Multiple independent credible sources
- Clear causal mechanism
- Limited counter-evidence
- Convergence score >80%

**Output statement:**
> "High confidence: [prediction] based on [evidence summary]."

### Medium Confidence (60-80%)

**Required:**
- Clear direction with some disagreement
- Adequate sources with some gaps
- Plausible causal mechanism
- Manageable counter-evidence
- Convergence score 60-80%

**Output statement:**
> "Medium confidence: [prediction] with caveats [caveats]."

### Low Confidence (40-60%)

**Required:**
- Mixed signals among personas
- Limited or conflicting sources
- Unclear causal mechanism
- Significant counter-evidence
- Convergence score 40-60%

**Output statement:**
> "Low confidence: [prediction] but significant uncertainty. Monitor [indicators]."

### Research Needed (<40%)

**Triggers:**
- Insufficient sources
- Major events pending
- Extreme disagreement
- No clear causal mechanism
- Convergence score <40%

**Output statement:**
> "Insufficient data for prediction. Recommend gathering: [missing information]."

---

## 6. Bias Controls

### Required Perspective Diversity

Each debate must include:
- At least one opposing perspective (ensures adversarial analysis)
- At least one short-term/long-term view
- At least one optimistic/cautious voice
- At least 3 different analytical frameworks

### Analytical Framework Categories

| Framework | Personas | Select At Least |
|-----------|----------|-----------------|
| Historical/Precedent | 12 (Historian) | 1 |
| Implementation/Practical | 13 (Policy Implementation) | 1 |
| Economic/Market | 5, 6, 7, 10, 11 | 1 |
| Geopolitical/Power | 1, 2, 3, 4 | 1 (if relevant) |
| Social/Cultural | 14, 16, 17, 18 | 1 (if relevant) |

### Contrarian Edge Protection

**Protect lone dissenters when:**
- They provide strong evidence
- Identify overlooked risks
- Present logical counter-arguments

**Treatment:**
- Document dissenting view prominently
- Explain why majority may be wrong
- Flag as "key risk to monitor"

---

## 7. Output Quality Standards

### Required Output Elements

Every debate output MUST include:

1. **Executive Summary** (100 words max) - Prediction with probability
2. **Prediction** - Most likely outcome with probability and timeframe
3. **Analysis Quality Metrics** (table)
4. **Consensus Findings** (by agreement level)
5. **Causal Mechanism** - Why the outcome will occur
6. **Critical Uncertainties** (ranked by impact)
7. **Scenario Analysis** (with probabilities summing to 100%)
8. **Monitoring Framework** (actionable indicators)
9. **Evolution of Analysis** (positions eliminated/strengthened)
10. **Source Appendix** (with credibility)
11. **Limitations** (scope, data, methodological)
12. **Prediction Calibration** (for future assessment)

### Output Focus

The output is about **WHAT WILL HAPPEN** and **WHY**, not **WHAT SHOULD BE DONE**.

| Avoid | Use |
|-------|-----|
| "We recommend..." | "The most likely outcome is..." |
| "Should be done..." | "Is predicted to occur..." |
| Trading language | Prediction language |

---

## 8. Memory and Context Management

### Updating Memory

**After each debate:**
1. Store key conclusions in knowledge graph
2. Link related debates
3. Update macro outlook if significant
4. Flag outdated conclusions
5. Document debate retrospective for calibration

### Context Retrieval

**Before each debate:**
1. Read relevant macro thesis
2. Check for related prior debates
3. Retrieve relevant persona memory
4. Identify outdated assumptions

---

## 9. Error Recovery

### When Debate Stalls

**If no convergence after max rounds:**
1. Document areas of disagreement
2. Identify why no consensus (data gap? fundamental uncertainty?)
3. Output multiple viable scenarios with probabilities
4. Recommend next steps (more data, time resolution, etc.)

### When Sources Conflict

**Hierarchy of credibility:**
1. Official data > Analysis > Opinion
2. Recent > Stale
3. Primary source > Secondary reporting
4. Multiple independent sources > Single source

**Output:**
> "Conflicting sources: [Summarize conflict]. Weighting toward [more credible source] but acknowledging uncertainty."

---

## 10. Quality Gate Enforcement

**See `quality-gates.md` for:**
- Pre-Debate Quality Check (with stop rule)
- Post-Debate Quality Scorecard (15-item checklist)
- Convergence Tracking Standards
- Meta-Learning Loop template

---

## 11. Evidence Quality Standards by Topic Type

| Topic Type | Preferred Sources | Recency Requirement |
|-----------|------------------|---------------------|
| Monetary Policy | Central bank statements, FOMC minutes, Fed speeches | <14 days |
| Geopolitics | Major news wires, government statements, think tanks | <7 days |
| Economic Data | Official releases (BLS, BEA, etc.) | <30 days |
| Technology Policy | Company filings, regulatory announcements, tech news | <14 days |
| Social/Cultural | Academic studies, reputable surveys, established news | <90 days |
| Historical Analysis | Academic histories, archival sources, established historians | N/A |
