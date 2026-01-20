# Debate Constraints Reference

Quality standards, factual accuracy requirements, and persona interaction rules.

---

## Factual Accuracy Requirements

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

### Handling Uncertainty

When data is uncertain or conflicting:

```markdown
**Data Conflict:**
- Source A claims X
- Source B claims Y
- Resolution: [Explain discrepancy, choose more credible source, or note uncertainty]
```

---

## Persona Interaction Rules

### Challenge Requirements

**Every persona MUST:**
1. Challenge at least one other persona's position
2. Be specific about the disagreement
3. Provide counter-evidence or reasoning
4. Specify what would change their mind

**Valid challenge format:**
```
TO: [Persona Name]
DISAGREE: [Specific claim or conclusion]
REASON: [Counter-evidence or logic]
EVIDENCE NEEDED: [What would change my mind]
```

**Invalid challenges:**
- Vague disagreements ("I think you're wrong")
- Personal attacks
- Challenges without evidence
- Moving goalposts

### Response Requirements

**Challenged persona MUST:**
1. Address the specific challenge
2. Provide justification OR concede
3. Cite evidence for justification
4. Acknowledge weaknesses in their position

**Valid response format:**
```
RESPONSE TO: [Persona Name]
JUSTIFICATION: [Evidence supporting original position]
ACKNOWLEDGMENT: [Any weaknesses or limits in the argument]
OR
CONCESSION: [Admit the point cannot be defended; retract claim]
```

### Concession Rules

**When to concede:**
- Cannot provide supporting evidence
- Counter-evidence is stronger
- Original claim was based on incorrect data
- Realized logical flaw in position

**Concession format:**
```
CONCESSION: I acknowledge [specific point] is incorrect/weak.
RETRACTION: I retract my claim about [specific claim].
REVISED POSITION: [New position based on better understanding]
```

**NOT a concession:**
- "I see your point but..." (deflection)
- "That's one way to look at it" (evasion)
- Changing the subject

---

## Veto Power (Reality Checks)

### Common Ground Vetoes

Any persona can trigger a **reality check veto** when:

**Factual Error:**
- Claim contradicts well-established facts
- Data is grossly misstated
- Source is misrepresented

**Logic Error:**
- Circular reasoning
- Non sequitur conclusions
- False equivalence

**Anachronism:**
- Applying past patterns without context differences
- Ignoring structural changes

**Veto format:**
```
REALITY CHECK VETO: [Persona's claim]
REASON: [Why this is factually/logically incorrect]
CORRECTION: [Accurate information]
```

### Handling Vetoes

**When veto is triggered:**
1. Pause debate
2. Evaluate veto validity
3. If valid: Persona must correct claim
4. If invalid: Veto is overridden with justification

---

## Confidence Thresholds

### High Confidence (80%+)

**Required:**
- Strong consensus across personas
- Multiple independent credible sources
- Clear causal mechanism
- Limited counter-evidence

**Output statement:**
> "High confidence: [conclusion] based on [evidence summary]."

### Medium Confidence (60-80%)

**Required:**
- Clear direction with some disagreement
- Adequate sources with some gaps
- Plausible mechanism
- Manageable counter-evidence

**Output statement:**
> "Medium confidence: [conclusion] with caveats [caveats]."

### Low Confidence (40-60%)

**Required:**
- Mixed signals among personas
- Limited or conflicting sources
- Unclear mechanism
- Significant counter-evidence

**Output statement:**
> "Low confidence: [conclusion] but significant uncertainty. Monitor [indicators]."

### Research Needed (<40%)

**Triggers:**
- Insufficient sources
- Major events pending
- Extreme disagreement
- No clear mechanism

**Output statement:**
> "Insufficient data for conclusion. Recommend gathering: [missing information]."

---

## Bias Controls

### Required Perspective Diversity

Each debate must include:
- At least one bullish/bearish perspective
- At least one short-term/long-term view
- At least one optimistic/cautious voice

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

## Output Quality Standards

### Required Output Elements

Every debate output MUST include:

1. **Executive Summary** (3-4 sentences)
2. **Points of Agreement** (consensus findings)
3. **Points of Disagreement** (unresolved disputes)
4. **Scenario Analysis** (base/bull/bear cases)
5. **Confidence Level** (with justification)
6. **Key Indicators to Monitor**
7. **Sources** (with credibility assessment)

### Prohibited Output

- **No:** "We recommend buying/holding/selling"
- **Yes:** "The outlook suggests [tailwinds/headwinds]"
- **No:** Specific price targets
- **Yes:** Probability ranges for scenarios
- **No:** Definitive predictions without qualifications
- **Yes:** Conditional analysis with confidence levels

---

## Memory and Context Management

### Updating Memory

**After each debate:**
1. Store key conclusions in knowledge graph
2. Link related debates
3. Update macro outlook if significant
4. Flag outdated conclusions

### Context Retrieval

**Before each debate:**
1. Read relevant macro thesis
2. Check for related prior debates
3. Retrieve relevant persona memory
4. Identify outdated assumptions

---

## Error Recovery

### When Debate Stalls

**If no convergence after max rounds:**
1. Document areas of disagreement
2. Identify why no consensus (data gap? fundamental uncertainty?)
3. Output "Split Decision" with both perspectives
4. Recommend next steps (more data, time resolution, etc.)

### When Sources Conflict

**Hierarchy of credibility:**
1. Official data > Analysis > Opinion
2. Recent > Stale
3. Primary source > Secondary reporting
4. Multiple independent sources > Single source

**Output:**
> "Conflicting sources: [Summarize conflict]. Weighting toward [more credible source] but acknowledging uncertainty."
