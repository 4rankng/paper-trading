#!/usr/bin/env python3
"""
CSV Reader - Read and analyze CSV files.

Usage:
    python read_csv.py --path data.csv
    python read_csv.py --path data.csv --head 10
    python read_csv.py --path data.csv --filter "price > 100" --json
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean


def read_csv(path: str, head: int = None, tail: int = None,
             columns: str = None, filter_expr: str = None,
             sort: str = None, stats: bool = False) -> dict:
    """Read and process CSV file.

    Args:
        path: Path to CSV file
        head: Number of rows from start
        tail: Number of rows from end
        columns: Comma-separated columns to select
        filter_expr: Filter expression
        sort: Column to sort by (prefix - for desc)
        stats: Show statistics

    Returns:
        Dict with metadata and rows
    """
    path_obj = Path(path)
    if not path_obj.exists():
        return {"error": f"File not found: {path}"}

    try:
        # Try pandas first for advanced features
        if filter_expr or stats:
            return _read_with_pandas(path, head, tail, columns, filter_expr, sort, stats)
        else:
            return _read_with_csv(path, head, tail, columns, sort)
    except Exception as e:
        return {"error": f"Failed to read CSV: {str(e)}"}


def _read_with_csv(path: str, head: int = None, tail: int = None,
                   columns: str = None, sort: str = None) -> dict:
    """Read using built-in csv module."""
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    # Select columns
    if columns:
        col_list = [c.strip() for c in columns.split(",")]
        rows = [{k: v for k, v in row.items() if k in col_list} for row in rows]
        headers = [h for h in headers if h in col_list]

    # Sort
    if sort:
        reverse = sort.startswith("-")
        sort_key = sort.lstrip("-")
        rows = sorted(rows, key=lambda x: float(x.get(sort_key, 0)), reverse=reverse)

    # Head/tail
    if head:
        rows = rows[:head]
    elif tail:
        rows = rows[-tail:]

    return {
        "metadata": {
            "rows": len(list(csv.DictReader(open(path)))),
            "columns": len(headers),
            "headers": headers
        },
        "rows": rows
    }


def _read_with_pandas(path: str, head: int = None, tail: int = None,
                      columns: str = None, filter_expr: str = None,
                      sort: str = None, stats: bool = False) -> dict:
    """Read using pandas for advanced features."""
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas not installed. Run: pip install pandas"}

    df = pd.read_csv(path)

    # Filter
    if filter_expr:
        df = df.query(filter_expr)

    # Select columns
    if columns:
        col_list = [c.strip() for c in columns.split(",")]
        df = df[[c for c in col_list if c in df.columns]]

    # Sort
    if sort:
        reverse = sort.startswith("-")
        sort_key = sort.lstrip("-")
        df = df.sort_values(by=sort_key, ascending=not reverse)

    # Head/tail
    if head:
        df = df.head(head)
    elif tail:
        df = df.tail(tail)

    result = {
        "metadata": {
            "rows": len(df),
            "columns": len(df.columns),
            "headers": list(df.columns)
        },
        "rows": df.to_dict("records")
    }

    # Statistics
    if stats:
        result["stats"] = {}
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                result["stats"][col] = {
                    "count": len(series),
                    "mean": float(series.mean()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "std": float(series.std()) if len(series) > 1 else 0
                }

    return result


def format_output(result: dict, max_width: int = 120) -> str:
    """Format result as readable text.

    Args:
        result: Result dict from read_csv()
        max_width: Max column width

    Returns:
        Formatted string
    """
    if "error" in result:
        return f"Error: {result['error']}"

    output = []

    # Metadata
    meta = result.get("metadata", {})
    output.append(f"rows: {meta.get('rows', 0)} | columns: {meta.get('columns', 0)}")

    # Statistics
    if "stats" in result:
        output.append("\n## Statistics")
        for col, stats in result["stats"].items():
            output.append(f"\n{col}")
            output.append(f"  count: {stats['count']}")
            output.append(f"  mean: {stats['mean']:.2f}")
            output.append(f"  min: {stats['min']:.2f}")
            output.append(f"  max: {stats['max']:.2f}")
            if stats['std']:
                output.append(f"  std: {stats['std']:.2f}")

    # Rows as table
    if result.get("rows"):
        headers = list(result["rows"][0].keys()) if result["rows"] else []
        if headers:
            # Calculate column widths
            widths = {h: min(max_width, len(str(h))) for h in headers}
            for row in result["rows"]:
                for h in headers:
                    val = str(row.get(h, ""))
                    widths[h] = min(max_width, max(widths[h], len(val)))

            # Header
            header_line = " | ".join(h.ljust(widths[h]) for h in headers)
            output.append(header_line)

            # Rows
            for row in result["rows"]:
                row_line = " | ".join(str(row.get(h, "")).ljust(widths[h])[:widths[h]] for h in headers)
                output.append(row_line)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Read and analyze CSV files")
    parser.add_argument("--path", required=True, help="Path to CSV file")
    parser.add_argument("--head", type=int, help="Show first N rows")
    parser.add_argument("--tail", type=int, help="Show last N rows")
    parser.add_argument("--columns", help="Comma-separated columns to select")
    parser.add_argument("--filter", help="Filter expression (e.g., 'price > 100')")
    parser.add_argument("--sort", help="Sort by column (prefix - for desc)")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Save to file")

    args = parser.parse_args()

    # Read CSV
    result = read_csv(
        args.path,
        head=args.head,
        tail=args.tail,
        columns=args.columns,
        filter_expr=args.filter,
        sort=args.sort,
        stats=args.stats
    )

    # Output
    if args.json:
        text = json.dumps(result, indent=2, default=str)
    else:
        text = format_output(result)

    if args.output:
        Path(args.output).write_text(text)
        print(f"Output saved to: {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
