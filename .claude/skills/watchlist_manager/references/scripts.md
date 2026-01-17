# Watchlist Manager Scripts Reference

Complete documentation for watchlist management.

## watchlist_manager.py

Main script for all watchlist operations (search, add, update, remove, summary).

### Search Operations

#### Search by Ticker
```bash
python scripts/watchlist_manager.py --ticker PYPL
```

#### Batch Search
```bash
python scripts/watchlist_manager.py --tickers PYPL,NVDA,TCOM
```

#### Filter by Sector
```bash
python scripts/watchlist_manager.py --sector "Technology"
```

#### Filter by Priority
```bash
python scripts/watchlist_manager.py --priority HIGH
```

#### Filter by Risk Level
```bash
python scripts/watchlist_manager.py --risk MEDIUM
```

#### Top N Results
```bash
python scripts/watchlist_manager.py --top 10 --sort-by priority
```

#### Sort Options
- `--sort-by`: Options include `priority`, `added_date`, `ticker`, `risk`, `current_price`

#### Output Format
- `--format`: `json` or `human` (default: human)

### Add Stock

```bash
python scripts/watchlist_manager.py \
  --add \
  --ticker NVDA \
  --name "NVIDIA" \
  --sector "Technology" \
  --thesis "AI infrastructure leader"
```

#### Required Parameters
- `--ticker`: Stock symbol
- `--name`: Company name
- `--sector`: Sector classification
- `--thesis`: Investment thesis summary

#### Optional Parameters
- `--current-price`: Current trading price
- `--target-entry`: Desired entry price
- `--target-exit`: Target exit price
- `--invalidation-level`: Price level that invalidates thesis
- `--time-horizon`: Investment timeline (e.g., "6M", "1Y")
- `--risk-level`: Risk assessment (LOW, MEDIUM, HIGH)
- `--priority`: Priority level (LOW, MEDIUM, HIGH, URGENT)
- `--status`: Status (watch, buy, avoid, hold)
- `--thesis-status`: Thesis validation (PENDING, VALIDATING, VALIDATED, FAILED)
- `--position-size`: Target position size (%)
- `--notes`: Additional notes

### Update Stock

```bash
python scripts/watchlist_manager.py \
  --update \
  --ticker PYPL \
  --status buy \
  --priority HIGH
```

#### Behavior
- Updates any field except `ticker`
- Preserves existing fields not specified
- Updates `updated_date` timestamp

### Remove Stock

```bash
python scripts/watchlist_manager.py --remove --ticker PYPL
```

### Summary

```bash
python scripts/watchlist_manager.py --summary
```

#### Output
Statistics by:
- Sector distribution
- Priority levels
- Risk levels
- Thesis status
- Total count

## File Structure

**Location**: `watchlist.json`

**Format**: JSON array of watchlist objects

### Watchlist Object Structure

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "sector": "Technology",
  "thesis": "AI infrastructure leader, data center dominance",
  "current_price": 150.25,
  "target_entry": 145.00,
  "target_exit": 180.00,
  "invalidation_level": 135.00,
  "time_horizon": "6M",
  "risk_level": "MEDIUM",
  "priority": "HIGH",
  "status": "watch",
  "thesis_status": "VALIDATING",
  "position_size": 10.0,
  "notes": "Monitor earnings next month",
  "added_date": "2026-01-10",
  "updated_date": "2026-01-15"
}
```

## Field Definitions

### Status Values
- `watch`: Under observation, no action
- `buy`: Entry signal detected, consider buying
- `avoid`: Avoid, thesis or technical concerns
- `hold`: Already holding, monitor

### Thesis Status Values
- `PENDING`: Initial thesis, needs research
- `VALIDATING`: Actively researching, early progress
- `VALIDATED`: Thesis confirmed with evidence
- `FAILED`: Thesis proven invalid
- `TRANSFORMING`: Thesis evolving, new narrative

### Priority Values
- `LOW`: Interesting but not urgent
- `MEDIUM`: Worth monitoring regularly
- `HIGH`: High conviction, prioritize research
- `URGENT`: Immediate action required

### Risk Level Values
- `LOW`: Conservative, stable company
- `MEDIUM`: Moderate risk/reward
- `HIGH`: Speculative, high volatility

## Search and Filter Examples

### Find High Priority Tech Stocks
```bash
python scripts/watchlist_manager.py \
  --sector "Technology" \
  --priority HIGH \
  --top 10
```

### Find Stocks Near Entry Price
```bash
python scripts/watchlist_manager.py \
  --format json | \
  jq '.[] | select(.current_price <= .target_entry * 1.05)'
```

### Find Pending Validation
```bash
python scripts/watchlist_manager.py \
  --thesis-status PENDING,VALIDATING
```

### Find Recent Additions
```bash
python scripts/watchlist_manager.py \
  --sort-by added_date \
  --top 20
```

## Common Workflows

### Initial Stock Screening
```bash
# Check if stock already on watchlist
python scripts/watchlist_manager.py --ticker NVDA

# If not found, add to watchlist
python scripts/watchlist_manager.py --add --ticker NVDA ...
```

### Daily Watchlist Review
```bash
# Get summary of current state
python scripts/watchlist_manager.py --summary

# Get high priority items
python scripts/watchlist_manager.py --priority HIGH,URGENT

# Get buy signals
python scripts/watchlist_manager.py --status buy
```

### Thesis Validation Tracking
```bash
# Update thesis status after research
python scripts/watchlist_manager.py \
  --update \
  --ticker NVDA \
  --thesis-status VALIDATED

# Find stocks needing validation
python scripts/watchlist_manager.py --thesis-status PENDING
```
