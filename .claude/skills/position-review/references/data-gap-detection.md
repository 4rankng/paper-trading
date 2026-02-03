# Data Gap Detection Workflow

**Goal:** Ensure all necessary context is available BEFORE running the Position Review logic.

The "Inertia Principle" (Existing positions = VALID unless proven DEAD) requires knowing the *original reason* for holding the position. You cannot determine if a thesis is dead if you don't know what the thesis was.

## critical Data Points

For every position review, you must have:

1.  **Machine Type** (HYPE_MACHINE, EARNINGS_MACHINE, MEAN_REVERSION_MACHINE, SECULAR_GROWTH, etc.)
    *   *Why:* Determines the specific exit logic to apply.
2.  **Thesis Status** (PENDING, VALIDATING, VALIDATED, STRONGER, WARNING, DANGER, FAILED)
    *   *Why:* Determines if we are in "defense mode" or "growth mode".
3.  **Original Thesis / Entry Rationale**
    *   *Why:* To compare against current news/fundamentals.
4.  **Fundamental Score** (0-100)
    *   *Why:* Required for EARNINGS_MACHINE exit logic.

## Detection & Resolution Steps

### Step 1: Check `portfolio.json`
This is the authoritative source for active positions.

*   **Machine Type:** Check `holdings[].machine_type`.
*   **Thesis Status:** Check `holdings[].thesis_status`.
*   **Original Thesis:** Check `holdings[].thesis`.

### Step 2: Check Analytics Files
If data is missing from portfolio.json, check `analytics/{TICKER}/`.

*   `{TICKER}_investment_thesis.md`: Look for "Investment Thesis" section.
*   `{TICKER}_fundamental_analysis.md`: Look for Fundamental Score.

### Step 3: Fill Gaps with `ask` Skill
If critical data is still missing, you must ask the user *before* proceeding with the review.

**Use the `ask` skill to generate specific questions:**

| Missing Data | Question to Ask |
|--------------|-----------------|
| **Machine Type** | "Is {TICKER} a HYPE trade, EARNINGS investment, or SECULAR GROWTH play?" |
| **Entry Rationale** | "What was your original buy rationale for {TICKER}?" |
| **Thesis Status** | "Has the thesis for {TICKER} been validated yet?" |

### Defaults (If User is Unavailable)

If you cannot get an answer and must proceed:

*   **Default Machine Type:** `EARNINGS_MACHINE` (This is the most conservative classification for the Inertia Principle, requiring strong fundamentals to hold).
*   **Default Status:** `WARNING` (Assume caution if status is unknown).
