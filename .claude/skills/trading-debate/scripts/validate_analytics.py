#!/usr/bin/env python3
"""
Validate analytics files for trading-debate skill.

Checks:
1. Required files exist
2. Files are fresh (<24 hours old)
3. Files are not empty

Usage:
    python validate_analytics.py TICKER

Returns:
    0 if all valid, 1 if validation fails
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def validate_analytics(ticker: str, max_age_hours: int = 24) -> dict:
    """
    Validate analytics files for a ticker.

    Args:
        ticker: Stock ticker symbol
        max_age_hours: Maximum age in hours (default 24)

    Returns:
        dict with 'valid', 'errors', and 'warnings' keys
    """
    # Normalize ticker
    ticker = ticker.upper().strip()
    base_dir = Path.cwd()
    analytics_dir = base_dir / "analytics" / ticker

    # Required files
    required_files = [
        f"{ticker}_technical_analysis.md",
        f"{ticker}_fundamental_analysis.md",
        f"{ticker}_investment_thesis.md",
    ]

    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "files": {},
    }

    # Check each required file
    for filename in required_files:
        filepath = analytics_dir / filename

        if not filepath.exists():
            result["errors"].append(f"Missing: {filepath}")
            result["valid"] = False
            continue

        # Check file age
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        age = datetime.now() - mtime
        age_hours = age.total_seconds() / 3600

        result["files"][filename] = {
            "path": str(filepath),
            "age_hours": round(age_hours, 1),
            "mtime": mtime.isoformat(),
        }

        if age_hours > max_age_hours:
            result["warnings"].append(
                f"Stale: {filename} is {age_hours:.1f}h old (max {max_age_hours}h)"
            )

        # Check file not empty
        if filepath.stat().st_size == 0:
            result["errors"].append(f"Empty: {filename}")
            result["valid"] = False

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_analytics.py TICKER [MAX_AGE_HOURS]")
        sys.exit(1)

    ticker = sys.argv[1]
    max_age = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    result = validate_analytics(ticker, max_age)

    # Print results
    if result["valid"]:
        print(f"✓ Analytics files validated for {ticker}")
    else:
        print(f"✗ Validation failed for {ticker}")

    for error in result["errors"]:
        print(f"  ERROR: {error}")

    for warning in result["warnings"]:
        print(f"  WARNING: {warning}")

    for filename, info in result["files"].items():
        print(f"  {filename}: {info['age_hours']}h old")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
