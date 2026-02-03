---
name: read-csv
description: Read and analyze CSV files using Python. Use for: "read csv", "parse csv", "csv data", "open csv", "analyze csv", "csv summary", "csv statistics". Supports filtering, aggregation, head/tail preview, and JSON output.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
---

# CSV Reader - Quick Reference

Read, analyze, and extract insights from CSV files.

---

## Quick Start

```bash
# Read CSV with summary
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv

# Preview first N rows
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv --head 10

# Filter rows (WHERE clause)
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv --filter "column > 100"

# Select specific columns
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv --columns col1,col2

# Output as JSON
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv --json --output data.json

# Get statistics
python .claude/skills/read-csv/scripts/read_csv.py --path data.csv --stats
```

---

## When to Use

| Use | Don't Use |
|-----|-----------|
| Analyze price/financial CSVs | PDF files (use read-pdf) |
| Filter and aggregate data | Excel files (convert first) |
| Quick CSV inspection | |
| Convert CSV to JSON | |

---

## Available Scripts

**read_csv.py** - Main CSV reading script
- `--path` - CSV file path (required)
- `--head` - Show first N rows (default: 5)
- `--tail` - Show last N rows
- `--columns` - Comma-separated column names to select
- `--filter` - Filter expression (e.g., "price > 100")
- `--sort` - Sort by column (prefix with - for desc: "-date")
- `--stats` - Show column statistics
- `--json` - Output as JSON
- `--output` - Save to file

---

## Filter Syntax

Simple comparisons:
- `column > 100`
- `name == "AAPL"`
- `volume >= 1000000`

Combined with AND/OR:
- `price > 100 AND volume < 1000000`
- `symbol == "NVDA" OR symbol == "AMD"`

---

## Output Format

**Default mode:** Formatted table
```
rows: 1000 | columns: 6
date       | open   | high   | low    | close  | volume
2024-01-01 | 148.5  | 150.2  | 147.8  | 149.5  | 50000000
```

**Stats mode:** Column statistics
```
close
  count: 1000
  mean: 148.32
  min: 120.50
  max: 175.80
```

**JSON mode:** Structured data
```json
{"rows": [...], "metadata": {...}}
```

---

## Requirements

- Built-in csv module (no external deps for basic usage)
- pandas: `pip install pandas` (for advanced filtering/stats)

---

## Constraints

- Large files (>1M rows) may be slow
- Complex filters require pandas
- Headers must be present in first row
