# Game Theory Principles for Trading Debates

This document explains the game-theoretic foundations of the optimized debate framework.

---

## Core Objective

**Truth-seeking through adversarial analysis.**

The debate framework is designed to converge on the most probable correct trading decision by:
1. Forcing competing perspectives to engage
2. Penalizing low-quality arguments
3. Rewarding accuracy over time
4. Detecting convergence efficiently

---

## 1. Incentive Alignment

### Problem: Echo Chambers

Without proper incentives, agents may:
- Agree with consensus to avoid conflict
- Make weak challenges that don't test positions
- Refuse to concede even when wrong

### Solution: Scoring System

Each persona earns a score:
```
score = (successful_challenges × 2) - (concessions × 1) - (failed_challenges × 0.5)
```

**Game-theoretic properties:**
- **Challenge quality matters**: Failed challenges penalize
- **Concessions hurt but not fatal**: -1 vs +2 for success
- **Participation required**: Must challenge to earn

### Nash Equilibrium

The dominant strategy is:
- Make specific, evidence-based challenges
- Concede when genuinely wrong (cut losses)
- Defend strongly when right (maximize reward)

---

## 2. Information Aggregation

### The Wisdom of Crowds

Independent opinions aggregate to truth when:
1. Opinions are diverse (different perspectives)
2. Opinions are independent (no herding)
3. Opinions are decentralized (different knowledge)
4. Mechanism exists to aggregate opinions

### Debate Framework Implementation

| Requirement | Implementation |
|-------------|----------------|
| Diversity | 10 distinct personas with different biases |
| Independence | Adversarial structure prevents herding |
| Decentralization | Each persona specializes |
| Aggregation | Bayesian weighted voting |

### Condorcet Jury Theorem

If each voter has >50% chance of being correct, and votes independently:
- More voters = higher probability of correct outcome
- Approaches 100% as N → ∞

**Our adaptation:**
- Personas have varying accuracy (tracked over time)
- Votes weighted by historical accuracy
- Low-accuracy voters penalized (muted)

---

## 3. Bayesian Epistemology

### Prior Belief

Before Round 1:
```
P(Buy) = 0.5
P(Sell) = 0.5
Confidence = 0.0
```

### Updating

After each round of challenges and responses:
```
P(Buy | Evidence) = weighted_votes_buy / total_weighted_votes
Confidence = |P(Buy) - 0.5| × 2
```

### Convergence

Stop when:
- **Confidence > 90%**: Sufficient certainty
- **Minimum rounds met**: Avoid premature stopping
- **Stagnation detected**: No new information

### Why This Works

- **Bayesian updating**: Mathematically optimal belief revision
- **Weighted votes**: Expert opinions count more
- **Early stopping**: Efficient resource use

---

## 4. Adversarial Red-Teaming

### The Short-Seller Role

Forced adversarial perspective prevents groupthink:

| Mechanism | Effect |
|-----------|--------|
| Must find bear case | Prevents bull echo chamber |
| Challenges others | Tests argument strength |
| Scored on success | Incentivizes quality criticism |

### Devil's Advocate

Similar principle applied to all personas:
- Each persona must challenge another
- Default: challenge most-disagreed view
- Result: weakest arguments eliminated

---

## 5. Mechanism Design

### Auto-Muting Mechanism

**Problem:** Low-quality participants waste rounds.

**Solution:** Mute personas with <30% challenge success rate.

**Game-theoretic effect:**
- Participation becomes costly if low-quality
- Forces personas to improve or be silenced
- Still allows voting (contribution limited, not zero)

### Revelation Principle

Agents should truthfully reveal their information.

**Our implementation:**
- Concessions explicitly tracked
- Weak defenses penalized
- Strong defenses rewarded
- Result: truth-telling incentivized

---

## 6. Efficiency Optimizations

### Parallel vs Sequential

**Sequential (traditional):**
- N personas → N challenges → N responses → N×N total actions
- Complexity: O(N²) per round
- Example: 10 personas = 90 actions

**Parallel (optimized):**
- N personas → N challenges → N responses
- Complexity: O(N) per round
- Example: 10 personas = 20 actions

**Token savings:** ~75% per round

### Fast Mode for Short Timeframes

For 1d-3d trades:
- Full debate overkill
- 3 critical agents sufficient
- Single round adequate
- CIO direct verdict

**Rationale:**
- Scalping decisions need speed
- Technicals dominate (Trend, Volume, Risk)
- Less uncertainty = less debate needed

---

## 7. Learning and Adaptation

### Historical Accuracy Tracking

Track for each persona:
- Challenge success rate
- Vote correctness
- Concession rate

### Weighted Voting

After 10+ debates:
- High-accuracy personas get more weight
- Low-accuracy personas get less weight
- New personas start at baseline (0.5)

**Formula:**
```
weight = 0.5 + (accuracy - 0.5) × influence_factor
```

### Cold Start Problem

Before 10 debates per persona:
- Use equal weights (0.5)
- Unbiased aggregation
- Transition to weighted as data accumulates

---

## 8. Truth-Seeking Properties

### Convergence Guarantees

Under reasonable assumptions:
1. Diverse perspectives → all angles considered
2. Adversarial challenges → weak arguments eliminated
3. Evidence-based scoring -> truth incentivized
4. Bayesian updating → beliefs converge to truth

### Known Limitations

| Limitation | Mitigation |
|------------|------------|
| LLM hallucinations | Analytics data as source of truth |
| Same data, same conclusion | Multiple personas, different lenses |
| No real-world feedback | Outcome tracking for learning |
| Market regime shifts | Macro context integration |

---

## 9. Configuration Tunables

All parameters in `config.json`:

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `mute_threshold` | 0.30 | Balance quality vs participation |
| `min_challenges_before_mute` | 3 | Allow learning curve |
| `confidence_threshold` | 0.90 | High certainty required |
| `min_debates_for_weighting` | 10 | Cold start period |
| `scalping_fast_threshold_days` | 3 | Fast mode cutoff |

### Tuning Guidance

- **Higher mute threshold** (0.40): More lenient, slower convergence
- **Lower mute threshold** (0.20): More aggressive, risk of false positives
- **Higher confidence threshold** (0.95): More rounds, higher certainty
- **Lower confidence threshold** (0.85): Faster, more errors

---

## 10. Monitoring and Debugging

### Health Metrics

```bash
# View all persona stats
python .claude/skills/trading-debate/scripts/persona_tracker.py --stats

# Check specific persona
python .claude/skills/trading-debate/scripts/persona_tracker.py --persona "Trend Architect"

# Test challenge scorer
python .claude/skills/trading-debate/scripts/challenge_scorer.py --test

# Simulate Bayesian convergence
python .claude/skills/trading-debate/scripts/bayesian_updater.py --simulate
```

### Red Flags

| Metric | Warning Level | Action |
|--------|---------------|--------|
| Concession rate | <10% | Personas too stubborn, lower mute threshold |
| Concession rate | >40% | Challenges too weak, raise quality standards |
| Rounds to convergence | Always max | Convergence failing, check confidence calc |
| Mute rate | >20% | Threshold too aggressive, lower to 0.25 |
| Confidence at convergence | <70% | Low-certainty decisions, increase min rounds |

---

## References

- **Condorcet Jury Theorem**: Collective intelligence under independent voting
- **Bayesian Epistemology**: Optimal belief updating
- **Mechanism Design**: Incentive-aligned systems
- **Adversarial Debating**: "AI Debate" (Irving et al., 2018)
- **Prediction Markets**: Aggregating dispersed information

---

## Summary

The optimized debate framework applies game-theoretic principles to achieve truth-seeking:

| Principle | Implementation |
|-----------|----------------|
| Incentive alignment | Scoring system, muting, weighted voting |
| Information aggregation | Diverse personas, Bayesian updating |
| Adversarial testing | Forced challenges, Short-Seller role |
| Efficiency | Parallel challenges, fast mode |
| Learning | Accuracy tracking, outcome feedback |
| Convergence | Bayesian confidence, early stopping |

**Result:** A debate system that converges on high-probability trading decisions efficiently.
