#!/usr/bin/env python3
"""
Migrate watchlist from old schema to new Quick-Glance schema.

Old Schema:
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "sector": "Technology",
  "thesis": "...",
  "current_price": 150,
  "target_entry": "140",
  "target_exit": "200",
  "invalidation_level": "130",
  "risk_level": "HIGH",
  "priority": "HIGH",
  "status": "watch",
  ...
}

New Schema:
{
  "meta": {
    "ticker": "NVDA",
    "name": "NVIDIA Corporation",
    "sector": "Technology",
    "industry": "",
    "added_date": "2026-01-16",
    "last_updated": "2026-01-17"
  },
  "score_card": {
    "total_score": 0,
    "max_score": 100,
    "rating": "C",
    "components": {}
  },
  "signal": {
    "action": "WATCH",
    "conviction": "MODERATE",
    "priority": "HIGH",
    "alternatives": []
  },
  "setup": {
    "current_price": 150,
    "target_entry": 140,
    "target_exit": 200,
    "invalidation": 130,
    "ratios": {}
  },
  "key_factors": {
    "flags": [],
    "catalysts": [],
    "breakeven_est": null
  }
}
"""

import json
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(*current_path.parts[:current_path.parts.index("skills") - 2])


def map_status_to_action(status: str) -> str:
    """Map old status field to new action field."""
    status_upper = status.upper()
    
    mapping = {
        "watch": "WATCH",
        "buy": "BUY",
        "avoid": "AVOID",
        "hold": "HOLD",
        "sell": "SELL",
        "trim": "TRIM"
    }
    
    return mapping.get(status_upper, "WATCH")


def migrate_entry(old_entry: dict) -> dict:
    """Migrate a single watchlist entry from old to new schema."""
    
    # Extract old fields
    ticker = old_entry.get("ticker", "")
    name = old_entry.get("name", "")
    sector = old_entry.get("sector", "")
    thesis = old_entry.get("thesis", "")
    current_price = old_entry.get("current_price")
    target_entry = old_entry.get("target_entry")
    target_exit = old_entry.get("target_exit")
    invalidation_level = old_entry.get("invalidation_level")
    risk_level = old_entry.get("risk_level")
    priority = old_entry.get("priority", "MEDIUM")
    status = old_entry.get("status", "watch")
    added_date = old_entry.get("added_date", "2026-01-17")
    
    # Convert numeric prices
    if target_entry and isinstance(target_entry, str):
        try:
            target_entry = float(target_entry)
        except:
            target_entry = None
    
    if target_exit and isinstance(target_exit, str):
        try:
            target_exit = float(target_exit)
        except:
            target_exit = None
    
    if invalidation_level and isinstance(invalidation_level, str):
        try:
            invalidation_level = float(invalidation_level)
        except:
            invalidation_level = None
    
    # Calculate ratios if we have price data
    ratios = {}
    if current_price and target_exit:
        entry_price = target_entry if target_entry else current_price
        upside = round(((target_exit - entry_price) / entry_price) * 100, 1)
        ratios["upside_potential_pct"] = upside
        
        if invalidation_level:
            downside = round(((entry_price - invalidation_level) / entry_price) * 100, 1)
            ratios["downside_risk_pct"] = downside
            
            if upside > 0 and downside > 0:
                ratios["risk_reward_ratio"] = round(upside / downside, 2)
    
    # Map to new schema
    new_entry = {
        "meta": {
            "ticker": ticker,
            "name": name,
            "sector": sector,
            "industry": "",
            "added_date": added_date,
            "last_updated": "2026-01-17"
        },
        "score_card": {
            "total_score": 50,  # Default neutral score
            "max_score": 100,
            "rating": "C",  # Default rating
            "components": {}  # Empty components to be filled in later
        },
        "signal": {
            "action": map_status_to_action(status),
            "conviction": "MODERATE",  # Default conviction
            "priority": priority.upper(),
            "alternatives": []  # Could be parsed from thesis
        },
        "setup": {
            "current_price": current_price,
            "target_entry": target_entry,
            "target_exit": target_exit,
            "invalidation": invalidation_level,
            "ratios": ratios
        },
        "key_factors": {
            "flags": [],
            "catalysts": [],
            "breakeven_est": None
        }
    }
    
    # Remove None values
    def clean_none(obj):
        if isinstance(obj, dict):
            return {k: clean_none(v) for k, v in obj.items() if v is not None and v != {} and v != []}
        elif isinstance(obj, list):
            return [clean_none(item) for item in obj]
        return obj
    
    return clean_none(new_entry)


def main():
    """Main migration function."""
    project_root = get_project_root()
    watchlist_path = project_root / "watchlist.json"
    backup_path = project_root / "watchlist.backup.json"
    
    # Load existing watchlist
    print(f"Loading watchlist from: {watchlist_path}")
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        old_watchlist = json.load(f)
    
    print(f"Found {len(old_watchlist)} entries to migrate")
    
    # Create backup
    print(f"Creating backup at: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(old_watchlist, f, indent=2)
    
    # Migrate entries
    new_watchlist = []
    for i, old_entry in enumerate(old_watchlist, 1):
        print(f"\nMigrating {i}/{len(old_watchlist)}: {old_entry.get('ticker', 'UNKNOWN')}")
        new_entry = migrate_entry(old_entry)
        new_watchlist.append(new_entry)
        print(f"  → {new_entry['meta']['ticker']} - Action: {new_entry['signal']['action']}, Priority: {new_entry['signal']['priority']}")
    
    # Save migrated watchlist
    print(f"\nSaving migrated watchlist to: {watchlist_path}")
    with open(watchlist_path, 'w', encoding='utf-8') as f:
        json.dump(new_watchlist, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Migration complete!")
    print(f"   - Migrated {len(new_watchlist)} entries")
    print(f"   - Backup saved at: {backup_path}")
    print(f"\nNext steps:")
    print(f"   1. Review migrated entries")
    print(f"   2. Add score components (growth, value, profitability, momentum)")
    print(f"   3. Add flags and catalysts from thesis")
    print(f"   4. Update action signals based on analysis")


if __name__ == "__main__":
    main()
