# Debate Quality Gates

Pre-debate validation checks and post-debate quality assurance standards for truth-seeking predictions.

---

## 1. Pre-Debate Question Validation

**Execute BEFORE starting any debate.**

### Question Quality Assessment

The question is the foundation of the debate. Poor questions produce poor predictions.

```
Question: [The proposed debate topic]

Checklist:
[ ] Question is falsifiable (can be proven wrong)
[ ] Question is time-bounded (specific timeframe)
[ ] Question is about WHAT WILL HAPPEN (not what should happen)
[ ] Question is specific and measurable
[ ] Success criteria are defined (what constitutes the outcome?)
[ ] At least 5 high-credibility sources exist on this topic

**Stop Rule:** If <4 boxes checked, refine question before proceeding.
```

### Good vs. Bad Questions

| Bad Questions | Why Bad | Good Questions |
|---------------|---------|---------------|
| "What should the Fed do?" | Normative, not falsifiable | "Will the Fed cut rates by 25bp in January?" |
| "Is trade war good or bad?" | Subjective judgment | "Will tariff levels exceed 25% in 2026?" |
| "What's the future of AI?" | Too vague | "Will AI regulation pass Congress this year?" |
| "Will the economy recover?" | Undefined terms | "Will Q1 GDP show >2% growth?" |

### Quality Gate Questions

Before proceeding, ask:
1. **Is this question falsifiable?** Can we specify evidence that would prove each possible answer wrong?
2. **What timeframe are we predicting?** Is it specific enough?
3. **What evidence would change our mind?** Are there clear falsification criteria?
4. **Who cares about this answer?** Is there practical relevance?

### Source Validation Checklist

```
[ ] At least 5 sources identified
[ ] Sources are High or Medium credibility
[ ] At least 2 sources are recent (timeline depends on topic)
[ ] Sources represent diverse viewpoints
[ ] Conflicting sources have been identified
[ ] Data gaps are explicitly documented
```

**Source Credibility Tiers:**

| Tier | Examples | Weight |
|------|----------|--------|
| **High** | Central banks, government agencies, peer-reviewed research | 1.0x |
| **Medium** | Reuters, Bloomberg, FT, WSJ, established think tanks | 0.8x |
| **Low** | Partisan outlets, blogs, secondary reporting | 0.5x |
| **Exclude** | Social media, anonymous sources, predictions without methodology | 0x |

---

## 2. Enhanced Persona Selection Matrix

### Selection Criteria

| Requirement | Specification |
|-------------|---------------|
| **Count** | Minimum 5, Maximum 7 personas |
| **Diversity** | At least 3 different analytical frameworks |
| **Grounding** | Always include Historian (12) OR Policy Implementation (13) |
| **Adversarial** | At least 2 personas with opposing priors |

### Quality Filter for Each Persona

```
For each selected persona, verify:
[ ] Has domain expertise relevant to the question
[ ] Can cite specific evidence or frameworks
[ ] Holds a position that could be falsified
[ ] Represents a genuinely different worldview
```

### Conflict Potential Validation

Before finalizing persona selection, ask:

1. **Who will disagree with whom and why?**
2. **What are the cruxes of disagreement?**
3. **Can any existing sources resolve these disputes?**

If no conflicts identified, adjust selection.

**See `constraints.md` for Analytical Framework Categories table.**

---

## 3. Post-Debate Quality Scorecard

**Execute BEFORE finalizing output.**

### Process Quality

```
[ ] All selected personas contributed substantively
[ ] At least 15% of challenges resulted in concessions
[ ] Convergence score calculated and within expected range (60-80%)
[ ] At least 2 rounds of challenges completed
[ ] Each position cited specific evidence
[ ] No circular reasoning or unfalsifiable claims
```

### Content Quality

```
[ ] Answer is falsifiable (could be proven wrong)
[ ] Uncertainties explicitly acknowledged
[ ] Alternative scenarios considered
[ ] Monitoring framework is actionable
[ ] Sources are credible and recent (timeline appropriate)
[ ] Dissenting views fairly represented
```

### Prediction Quality

```
[ ] Prediction is specific with probability assigned
[ ] Causal mechanism clearly explained
[ ] Scenario probabilities sum to 100%
[ ] Leading indicators identified
[ ] Next review date specified
```

### Pass Threshold

**15/20 boxes checked minimum** to proceed to final output.

If failed:
1. Identify which boxes are unchecked
2. Run additional challenge round if needed
3. Gather additional sources if evidence gaps
4. Document remaining issues in "Limitations" section

---

## 4. Convergence Tracking Standards

### After Each Round

Document:

```markdown
## Round [N] Convergence Map

### Positions Eliminated (Falsified)
- [Persona] on [claim] - Conceded to [Challenger] due to [reason]

### Positions Strengthened (Withstood Challenges)
- [Persona] on [claim] - Defended against [challengers]

### Emerging Consensus
- [Claim] - Now supported by [N] personas

### Persistent Disagreements (Cruxes)
- [Persona A] vs [Persona B] on [fundamental issue]
  - A argues: [core claim]
  - B argues: [competing claim]
  - Crux: [What evidence/logic would resolve this?]

### Convergence Score: [X%]
(% of initial disagreements resolved or narrowed)
```

### Stop Conditions

1. **Convergence score >80%** (strong consensus reached)
2. **Convergence score unchanged for 2 consecutive rounds** (plateau)
3. **All remaining disagreements are crux-identified but unresolvable** with current evidence
4. **5 rounds completed**

### Target Convergence

| Convergence | Interpretation | Confidence Level |
|------------|----------------|------------------|
| 80%+ | Strong consensus - surviving position likely true | High |
| 60-80% | Clear direction - some uncertainty remains | Medium |
| 40-60% | Multiple viable scenarios | Low |
| <40% | Insufficient evidence - research needed | Research Needed |

---

## 5. Meta-Learning Loop

After each debate, document retrospective:

```markdown
## Debate Retrospective

**Debate:** [Topic]
**Date:** YYYY-MM-DD
**Confidence:** [Level]
**Prediction:** [What we predicted]

### What Worked
- [Persona selection, challenge quality, sources, etc.]

### What Didn't
- [Weak challenges, missing evidence, poor convergence, etc.]

### For Next Time
- [Adjustments to persona selection]
- [Additional sources to gather]
- [Questions to refine]

### Calibration
*(To be filled when outcome is known)*
- Was our confidence appropriate?
- Which personas were most/least accurate?
- Which indicators proved most predictive?
```

### Retrospective Categories

| Category | Questions to Ask |
|----------|------------------|
| **Persona Selection** | Were all voices needed? Who was missing? |
| **Information Quality** | Which sources were most valuable? What was missing? |
| **Challenge Quality** | Were challenges substantive? Did they drive convergence? |
| **Convergence** | Did consensus reflect reality or groupthink? |
| **Prediction Calibration** | If time passed, was confidence accurate? |

---

## 6. Evidence Quality Standards

**See `constraints.md` for:**
- Hierarchy of Evidence (7-tier credibility scale)
- Evidence Weighting Guidelines (with type examples)
- Conflicting Evidence Resolution (5-step process)
- Source Citation Format
- Evidence Quality Standards by Topic Type

---

## 7. Falsifiability Standards

Every position must include:

```markdown
**Falsification Criteria:** [What specific evidence would prove this wrong?]
```

**See `constraints.md` for additional falsifiability examples and standards.**

---

## 8. Stop Conditions for Low-Quality Debates

Halt debate and output "Research Needed" when:

| Condition | Action |
|-----------|--------|
| <3 credible sources available | Document gaps, stop |
| Major events pending that will resolve question | Wait, revisit |
| Data stale (timeline inappropriate for topic) | Refresh, retry |
| Conflicting sources with no resolution path | Document conflict, note uncertainty |
| Convergence <40% after 5 rounds | Output multiple scenarios with caveats |
| No falsifiable positions possible | Reframe question |

### "Research Needed" Output Format

```markdown
# Debate: [Topic]

**Status:** Research Needed

**Insufficient Data for Prediction.**

## Critical Gaps
1. [Missing information needed]
2. [Conflicting data that needs resolution]
3. [Pending events that will clarify]

## Recommended Research
- [Specific sources to gather]
- [Specific questions to investigate]
- [Timeline for revisit]

## Preliminary Assessment (Low Confidence)
[If any weak signals exist, document them with heavy caveats]
```

---

## 9. Prediction Quality Standards by Debate Type

| Debate Type | Target Convergence | Timeframe | Source Freshness |
|-------------|-------------------|-----------|------------------|
| Breaking Events (geopolitics) | 60-70% | Days-weeks | <7 days |
| Monetary Policy | 70-80% | Months | <14 days |
| Economic Forecasts | 60-75% | Quarters | <30 days |
| Social/Cultural Trends | 50-65% | Years | <90 days |
| Historical Analysis | 70-85% | N/A | N/A |

---

## 10. Truth-Seeking Principles

These principles distinguish truth-seeking debates from other forms of analysis:

1. **Falsifiability Over Certainty**
   - Every claim must specify what would prove it wrong
   - "I don't know" is better than false certainty
   - Probability ranges are preferred to binary predictions

2. **Causal Depth Over Surface Patterns**
   - Understanding *why* something will happen is as important as *what* will happen
   - Every prediction must include a causal mechanism
   - Historical precedents must be analyzed, not just cited

3. **Convergence as Truth Signal**
   - High consensus among diverse experts increases confidence
   - Surviving adversarial challenges is evidence of truth
   - Elimination of falsified positions is progress

4. **Calibration Over Confidence**
   - Track prediction accuracy over time
   - Being roughly right is better than being precisely wrong
   - Update beliefs based on outcomes

5. **Embrace Uncertainty**
   - Low-confidence truth is better than high-confidence error
   - Multiple scenarios are better than false precision
   - "Research needed" is a valid and important outcome

6. **Adversarial Rigor**
   - Include opposing analytical frameworks
   - Challenge assumptions, not just conclusions
   - Protect lone dissenters when they have strong evidence
