---
allowed-tools: Bash, Glob, Skill, Read, Write
description: Ask 5 factual questions about a ticker to inform an investment decision
argument-hint: [ticker]
---

## Objective

Generate 5 high-value, fact-based questions about {TICKER} to bridge information gaps for an investment decision.

## Prerequisites

**Read Existing Data**: Review `analytics/{TICKER}`, `news/{TICKER}`, and `trading_plans/{TICKER}`.
**Identify Gaps**: Formulate questions only for information not present in these files.

## Strict Parameters

- **Word Count**: Total output must be < 300 words
- **Content**: Verifiable facts, historical/current data, quantitative metrics, and official filings only
- **Tone**: Objective and evidence-based
- **Prohibitions**: No predictions, opinions, speculation, or subjective assessments

## Purpose

The responses will provide the hard evidence necessary to execute a data-driven investment strategy for {TICKER}.
