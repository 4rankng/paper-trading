#!/usr/bin/env python3
"""Batch classify unclassified stocks based on technical/fundamental analysis."""

import json
import os
import re

# Read watchlist to find unclassified stocks
with open('watchlist.json', 'r') as f:
    watchlist = json.load(f)

# Get unclassified stocks
unclassified = [s for s in watchlist if s.get('strategy') is None]

print(f"Found {len(unclassified)} unclassified stocks")
print()

# Strategy classification based on technical/fundamental data
CLASSIFICATIONS = {
    # Compounders - quality businesses
    "AAPL": {"strategy": "quality_growth", "hold": "12-24m", "fit": 85, "buy_score": 75},
    "STNG": {"strategy": "dividend_aristocrat", "hold": "1y+", "fit": 70, "buy_score": 95},
    "VAL": {"strategy": "quality_discount", "hold": "1y+", "fit": 75, "buy_score": 75},

    # Moonshots - high growth potential
    "RIG": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 72, "buy_score": 85},  # Uptrend, strong momentum
    "BA": {"strategy": "turnaround", "hold": "3-6m", "fit": 65, "buy_score": 100},  # Turnaround story
    "OXY": {"strategy": "quality_at_fair_price", "hold": "1y+", "fit": 60, "buy_score": 100},  # Berkshire-backed
    "BORR": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 68, "buy_score": 100},  # Uptrend
    "APLD": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 78, "buy_score": 100},  # Strong uptrend
    "DDOG": {"strategy": "quality_growth", "hold": "12-24m", "fit": 65, "buy_score": 75},  # Quality compounder
    "DNLI": {"strategy": "binary_event", "hold": "3-12m", "fit": 60, "buy_score": 90},  # Biotech binary
    "RIGL": {"strategy": "binary_event", "hold": "3-12m", "fit": 65, "buy_score": 100},  # Biotech
    "HALO": {"strategy": "binary_event", "hold": "3-12m", "fit": 70, "buy_score": 100},  # Biotech
    "IONQ": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 60, "buy_score": 50},  # Quantum
    "RGTI": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 62, "buy_score": 85},  # Quantum
    "BE": {"strategy": "quality_at_fair_price", "hold": "1y+", "fit": 60, "buy_score": 70},  # Hydrogen

    # FINAL 8 CLASSIFICATIONS (deep research completed)

    # COIN - Strong fundamentals: 43.7% margins, $9.77B cash, Base network 62% L2 share
    # Only profitable L2, institutional custody leader. Crypto beta play.
    "COIN": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 68, "buy_score": 65},

    # LAES - QS7001 PQC chip, CNSA 2.0 mandate Jan 2027, $200M+ pipeline
    # HYPE_MACHINE phenomenon, regulatory catalyst creates forced adoption window.
    "LAES": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 70, "buy_score": 100},

    # PONY - UE breakeven validated (Guangzhou), $1.4B cash post-IPO
    # Extreme valuation (60-80x P/S) but first to prove robotaxi unit economics.
    "PONY": {"strategy": "conditional", "hold": "conditional", "fit": 70, "buy_score": 100},

    # QUBT - Quantum software, extreme valuation 4,926x P/S, $556M cash fortress
    # Retail-driven, Reddit favorite. Below 60 fit threshold due to valuation.
    "QUBT": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 55, "buy_score": 60},  # Below threshold

    # RDW - Strong uptrend (72.7/100 technical), -70% margin, high debt 22x D/E
    # Speculative momentum trade only. Fundamental weakness offsets technical strength.
    "RDW": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 68, "buy_score": 100},

    # TSLA - EV/AI platform leader, DBS target $380, above 200-day MA
    # Sideways consolidation, strong fundamentals, high_growth EV play.
    "TSLA": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 70, "buy_score": 75},

    # WRD - Weak technicals (33.6/100), ARK accumulating at $8.56 support
    # $764M cash, analyst PT $13.13, 7-10x multibagger potential.
    "WRD": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 55, "buy_score": 70},  # Below threshold

    # BBAI - Unprofitable (-295% margin), high debt (18.5 D/E), downtrend
    # Below 60 fit threshold - keep unclassified until conditions improve.
    "BBAI": {"strategy": "trend_rider", "hold": "2w-3m", "fit": 45, "buy_score": 75},  # Below threshold
}

# Generate update commands
updates = []
for stock in unclassified:
    ticker = stock['ticker']
    if ticker in CLASSIFICATIONS:
        cls = CLASSIFICATIONS[ticker]
        strategy = cls['strategy']
        hold = cls['hold']
        fit = cls['fit']
        buy_score = cls['buy_score']

        # Only classify if fit >= 60
        if fit >= 60:
            print(f"{ticker}: {strategy} | {hold} | Fit: {fit} | BuyScore: {buy_score}")
            updates.append({
                'ticker': ticker,
                'strategy': strategy,
                'hold': hold,
                'fit': fit,
                'buy_score': buy_score
            })
        else:
            print(f"{ticker}: BELOW FIT THRESHOLD ({fit}) - keeping unclassified")
    else:
        print(f"{ticker}: NO CLASSIFICATION - needs analysis")

print()
print(f"=== {len(updates)} stocks to classify ===")

# Generate watchlist update commands
if updates:
    new_watchlist = []
    for stock in watchlist:
        ticker = stock['ticker']
        # Find if this stock has an update
        update = next((u for u in updates if u['ticker'] == ticker), None)
        if update:
            stock['strategy'] = update['strategy']
            stock['hold'] = update['hold']
            stock['fit'] = update['fit']
            if 'buy_score' in update:
                stock['buy_score'] = update['buy_score']
            stock['updated_at'] = '2026-01-29'
        new_watchlist.append(stock)

    # Save updated watchlist
    with open('watchlist.json', 'w') as f:
        json.dump(new_watchlist, f, indent=2)

    print(f"Updated watchlist.json with {len(updates)} classifications")
