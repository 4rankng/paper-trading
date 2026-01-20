# Macro Fetcher Scripts Reference

Complete documentation for all macro management scripts.

## create_macro_thesis.py

Create monthly macro thesis with economic overview and investment implications.

### Usage

```bash
python .claude/skills/macro_fetcher/scripts/create_macro_thesis.py --month 2026_01
```

### Parameters

- `--month`: Month in YYYY_MM format (required)
- `--stance`: Overall stance (RISK-ON/RISK-OFF/NEUTRAL) (optional)
- `--risk-level`: Risk level (HIGH/MEDIUM/LOW) (optional)

### Behavior

- Creates `macro/theses/macro_thesis_YYYY_MM.md`
- Includes template with key economic variables
- Sector implications table
- Investment implications section

## add_geopolitical_event.py

Add analysis for geopolitical events affecting markets.

### Usage

```bash
python .claude/skills/macro_fetcher/scripts/add_geopolitical_event.py \
  --topic "US-China Trade Tensions" \
  --impact HIGH \
  --sectors "technology,consumer" \
  --date 2026-01-15
```

### Parameters

- `--topic`: Event topic name (required)
- `--impact`: Impact level (HIGH/MEDIUM/LOW) (required)
- `--sectors`: Comma-separated affected sectors (optional)
- `--date`: Event date (YYYY-MM-DD) (optional, defaults to today)

### Behavior

- Creates `macro/geopolitical/YYYY_MM_topic.md`
- Auto-generates URL-safe slug from topic
- Includes event analysis template

## add_central_bank_update.py

Add central bank policy update.

### Usage

```bash
python .claude/skills/macro_fetcher/scripts/add_central_bank_update.py \
  --bank fed \
  --month 2026_01 \
  --decision hold \
  --rate 5.25
```

### Parameters

- `--bank`: Central bank (fed/ecb/boj/pboc) (required)
- `--month`: Month in YYYY_MM format (required)
- `--decision`: Policy decision (hold/hike/cut) (optional)
- `--rate`: Interest rate (optional)
- `--statement`: Key statement summary (optional)

### Behavior

- Creates `macro/central_banks/{bank}_YYYY_MM.md`
- Includes policy decision, rate, forward guidance
- Market reaction summary

## add_commodity_update.py

Add commodity price analysis.

### Usage

```bash
python .claude/skills/macro_fetcher/scripts/add_commodity_update.py \
  --commodity oil \
  --month 2026_01 \
  --trend bullish
```

### Parameters

- `--commodity`: Commodity name (oil/gold/copper/etc.) (required)
- `--month`: Month in YYYY_MM format (required)
- `--trend`: Price trend (bullish/bearish/neutral) (optional)
- `--price`: Current price (optional)

### Behavior

- Creates `macro/commodities/YYYY_MM_{commodity}.md`
- Supply/demand analysis
- Geopolitical factors affecting price

## list_macro.py

List all macro analysis files.

### Usage

```bash
# List all macro files
python .claude/skills/macro_fetcher/scripts/list_macro.py

# List by category
python .claude/skills/macro_fetcher/scripts/list_macro.py --category theses

# Latest N files
python .claude/skills/macro_fetcher/scripts/list_macro.py --limit 5
```

### Parameters

- `--category`: Filter by category (theses/geopolitical/central_banks/commodities/overview) (optional)
- `--limit`: Maximum files to show (optional)
