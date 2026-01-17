#!/usr/bin/env python3
"""
Parse timeframe strings for trading-debate skill.

Supported formats:
- 3d, 7d → Scalping/Day Trading (days)
- 2w, 4w → Swing Trading (weeks)
- 3m, 6m → Position Trading (months)
- 1y, 2y → Investment (years)

Usage:
    python parse_timeframe.py TIMEFRAME

Example:
    python parse_timeframe.py 3m
    → {"model": "position", "days": 90, "agents": 7}
"""

import sys
import re


def parse_timeframe(timeframe: str) -> dict:
    """
    Parse a timeframe string into trading model parameters.

    Args:
        timeframe: String like "3d", "2w", "6m", "1y"

    Returns:
        dict with model, days, agents, and description
    """
    # Match pattern: number + unit
    match = re.match(r"^(\d+(?:\.\d+)?)([dwmy])$", timeframe.lower().strip())

    if not match:
        return {
            "error": f"Invalid timeframe format: {timeframe}. Use Nd, Nw, Nm, or Ny"
        }

    value = float(match.group(1))
    unit = match.group(2)

    # Unit to days conversion
    unit_days = {
        "d": 1,      # days
        "w": 7,      # weeks
        "m": 30,     # months (approx)
        "y": 365,    # years
    }

    total_days = int(value * unit_days[unit])

    # Model selection based on timeframe
    if unit == "d" or total_days <= 7:
        model = "scalping"
        agents = 6
        model_name = "Scalping/Day Trading"
    elif unit == "w" or total_days <= 30:
        model = "swing"
        agents = 10
        model_name = "Swing Trading"
    elif unit == "m" or total_days <= 180:
        model = "position"
        agents = 7
        model_name = "Position Trading"
    else:
        model = "investment"
        agents = 5
        model_name = "Investment"

    return {
        "model": model,
        "model_name": model_name,
        "agents": agents,
        "days": total_days,
        "input": timeframe,
        "value": value,
        "unit": unit,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_timeframe.py TIMEFRAME")
        print("Example: python parse_timeframe.py 3m")
        sys.exit(1)

    result = parse_timeframe(sys.argv[1])

    if "error" in result:
        print(result["error"])
        sys.exit(1)

    print(f"Input: {result['input']}")
    print(f"Model: {result['model_name']} ({result['model']})")
    print(f"Agents: {result['agents']} personas")
    print(f"Duration: {result['days']} days")

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
