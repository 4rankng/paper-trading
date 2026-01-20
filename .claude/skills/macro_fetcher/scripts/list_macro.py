#!/usr/bin/env python3
"""
List all macro analysis files.
"""

import argparse
import os
from pathlib import Path


CATEGORIES = {
    "theses": "macro/theses",
    "geopolitical": "macro/geopolitical",
    "central_banks": "macro/central_banks",
    "commodities": "macro/commodities",
    "overview": "macro/overview",
}


def list_macro_files(category: str = None, limit: int = None):
    """List macro files by category."""
    results = []

    if category:
        if category not in CATEGORIES:
            print(f"Invalid category. Choose from: {', '.join(CATEGORIES.keys())}")
            return
        categories = {category: CATEGORIES[category]}
    else:
        categories = CATEGORIES

    for cat, path in categories.items():
        if os.path.exists(path):
            files = []
            for f in os.listdir(path):
                if f.endswith('.md'):
                    full_path = os.path.join(path, f)
                    mtime = os.path.getmtime(full_path)
                    files.append((f, mtime, full_path))
            files.sort(key=lambda x: x[1], reverse=True)
            results.extend([(cat, f[0], f[2]) for f in files])

    # Sort globally by modification time
    if not category:
        results.sort(key=lambda x: os.path.getmtime(x[2]), reverse=True)

    # Apply limit
    if limit:
        results = results[:limit]

    return results


def main():
    parser = argparse.ArgumentParser(
        description="List macro analysis files"
    )
    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()),
        help="Filter by category"
    )
    parser.add_argument("--limit", type=int, help="Maximum files to show")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                       help="Output format")
    args = parser.parse_args()

    results = list_macro_files(args.category, args.limit)

    if args.format == "json":
        import json
        output = []
        for cat, filename, filepath in results:
            output.append({
                "category": cat,
                "filename": filename,
                "path": filepath
            })
        print(json.dumps(output, indent=2))
    else:
        if not results:
            print("No macro files found.")
            return

        print("Macro Analysis Files:")
        print("-" * 60)
        for cat, filename, filepath in results:
            rel_path = os.path.relpath(filepath)
            mtime = os.path.getmtime(filepath)
            from datetime import datetime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            print(f"[{cat:15s}] {filename:40s} ({mtime_str})")


if __name__ == "__main__":
    main()
