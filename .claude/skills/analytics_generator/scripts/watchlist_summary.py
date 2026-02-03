#!/usr/bin/env python3
"""
Watchlist summary after buy score reevaluation.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
watchlist = json.load(open(PROJECT_ROOT / "watchlist.json"))

# Count by classification
class_counts = {}
action_counts = {}
for s in watchlist:
    cls = s.get('classification', 'Unknown')
    act = s.get('recommended_action', 'Unknown')
    class_counts[cls] = class_counts.get(cls, 0) + 1
    action_counts[act] = action_counts.get(act, 0) + 1

print('WATCHLIST REEVALUATION SUMMARY')
print('=' * 60)
print(f'Total Stocks: {len(watchlist)}')
print()

print('By Classification:')
for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
    print(f'  {cls}: {count}')
print()

print('By Action:')
for act, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
    print(f'  {act}: {count}')
print()

# Score distribution
scores = [s.get('buy_score', 0) for s in watchlist]
avg_score = sum(scores) / len(scores) if scores else 0
print(f'Average Buy Score: {avg_score:.1f}')
print(f'Highest Score: {max(scores) if scores else 0}')
print(f'Lowest Score: {min(scores) if scores else 0}')
print()

# Strong Buy list
strong_buys = [s for s in watchlist if s.get('classification') == 'Strong Buy']
print(f'STRONG BUYS ({len(strong_buys)}):')
print('-' * 60)
for s in strong_buys:
    notes = s.get('notes', '')[:40]
    print(f'  {s["ticker"]:<6} {s.get("buy_score", 0):>5.1f}  ${s.get("price", 0):>8.2f}  {notes}')

print()
print('BUY SIGNALS (Score 60-74):')
print('-' * 60)
buys = [s for s in watchlist if s.get('classification') == 'Buy']
for s in buys[:20]:
    notes = s.get('notes', '')[:40]
    print(f'  {s["ticker"]:<6} {s.get("buy_score", 0):>5.1f}  ${s.get("price", 0):>8.2f}  {notes}')
if len(buys) > 20:
    print(f'  ... and {len(buys) - 20} more')

print()
print('AVOID/WATCH LIST (Score < 45):')
print('-' * 60)
weak = [s for s in watchlist if s.get('buy_score', 0) < 45]
for s in weak[:20]:
    print(f'  {s["ticker"]:<6} {s.get("buy_score", 0):>5.1f}  {s.get("classification", "N/A"):<15} ${s.get("price", 0):>8.2f}')
if len(weak) > 20:
    print(f'  ... and {len(weak) - 20} more')
