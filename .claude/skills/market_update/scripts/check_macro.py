#!/usr/bin/env python3
"""
Check macroeconomic context and market sentiment.

This script fetches CNN Fear & Greed Index and reads latest macro thesis.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude"))

from shared.data_access import get_file_age_hours


def get_latest_macro_thesis() -> Optional[Dict]:
    """
    Get latest macro thesis from macro/theses/ directory.

    Returns:
        Dict with stance, risk_level, summary, date or None if not found
    """
    macro_dir = project_root / "filedb" / "macro" / "theses"

    if not macro_dir.exists():
        return None

    # Find latest macro thesis file
    thesis_files = sorted(macro_dir.glob("macro_thesis_*.md"), reverse=True)

    if not thesis_files:
        return None

    latest_file = thesis_files[0]

    try:
        content = latest_file.read_text()

        # Extract overall stance
        stance_match = re.search(r'\*\*Overall Stance:\*\*\s*(RISK-ON|RISK-OFF|NEUTRAL)', content)
        stance = stance_match.group(1) if stance_match else "UNKNOWN"

        # Extract risk level
        risk_match = re.search(r'\*\*Risk Level:\*\*\s*(HIGH|MEDIUM|LOW)', content)
        risk_level = risk_match.group(1) if risk_match else "UNKNOWN"

        # Extract executive summary (first paragraph under Executive Summary)
        summary_match = re.search(r'## Executive Summary\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

        # Clean up summary (remove markdown formatting)
        summary = re.sub(r'\*\*', '', summary)
        summary = summary[:200] + "..." if len(summary) > 200 else summary

        return {
            "stance": stance,
            "risk_level": risk_level,
            "summary": summary,
            "date": latest_file.stem.split("_")[-1],  # Extract YYYY_MM from filename
            "age_days": get_file_age_hours(latest_file) / 24,
            "path": str(latest_file)
        }
    except Exception as e:
        print(f"Warning: Error reading macro thesis: {e}", file=sys.stderr)
        return None


def get_fear_and_greed() -> Optional[Dict]:
    """
    Get CNN Fear & Greed Index.

    NOTE: This is a placeholder. In the actual skill invocation,
    the LLM agent will use webReader tool to fetch the Fear & Greed index.

    Returns:
        Dict with value, label, change or None
    """
    # This function is called from the script, but the actual
    # webReader call will be done by the LLM agent when invoking the skill.
    return None


def get_macro_context() -> Dict:
    """
    Get complete macroeconomic context.

    Returns:
        Dict with fear_greed, macro_thesis, and warnings
    """
    result = {
        "fear_greed": {
            "value": None,
            "label": None,
            "change": None,
            "available": False
        },
        "macro_thesis": {
            "stance": None,
            "risk_level": None,
            "summary": None,
            "date": None,
            "available": False
        },
        "warnings": []
    }

    # Get macro thesis
    thesis = get_latest_macro_thesis()
    if thesis:
        result["macro_thesis"] = {
            "stance": thesis["stance"],
            "risk_level": thesis["risk_level"],
            "summary": thesis["summary"],
            "date": thesis["date"],
            "available": True,
            "age_days": thesis["age_days"]
        }

        # Check if thesis is stale
        if thesis["age_days"] > 7:
            result["warnings"].append(f"Macro thesis is {thesis['age_days']:.0f} days old (last updated {thesis['date']})")
    else:
        result["warnings"].append("No macro thesis found in macro/theses/")

    # Fear & Greed will be fetched by LLM agent
    result["warnings"].append("Fear & Greed Index to be fetched by LLM agent")

    return result


def main():
    parser = argparse.ArgumentParser(description="Check macroeconomic context")
    args = parser.parse_args()

    result = get_macro_context()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
