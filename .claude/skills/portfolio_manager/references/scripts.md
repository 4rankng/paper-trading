# Portfolio Manager Scripts Reference

Complete documentation for all portfolio and trade management scripts.

## get_portfolio.py

Return complete portfolio state with holdings, cash, P&L, and summary statistics.

### Usage

```bash
python scripts/get_portfolio.py
```

### Output

JSON format with:
- `holdings`: Array of position objects
- `cash`: Current cash balance and reserve
- `portfolio_summary`: Total value, P&L, performance metrics
- `metadata`: Last updated timestamp, version

**Output options**: `--format json` (default) or `--format human`

## add_holding.py

Add new position to portfolio with weighted average cost basis calculation.

### Usage

```bash
python scripts/add_holding.py \
  --ticker NVDA \
  --shares 100 \
  --price 150.25 \
  --thesis-status PENDING
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--shares`: Number of shares (required)
- `--price`: Purchase price per share (required)
- `--thesis-status`: Thesis validation status (options: PENDING, VALIDATING, STRONGER, WARNING, DANGER)

### Behavior

- Calculates cost basis (shares × price)
- Updates cash balance (deducts cost)
- Adds to holdings array
- Creates portfolio_summary if first holding
- Uses file locking to prevent concurrent modification

## remove_holding.py

Remove position (full or partial) from portfolio.

### Usage

```bash
# Full position sale
python scripts/remove_holding.py \
  --ticker LAES \
  --shares 5000 \
  --action SELL

# Partial position trim
python scripts/remove_holding.py \
  --ticker NVDA \
  --shares 25 \
  --action TRIM
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--shares`: Number of shares to remove (required)
- `--action`: Type of removal (options: SELL, TRIM) (required)

### Behavior

**SELL**: Removes entire position, adds cash from sale
**TRIM**: Removes partial shares, updates cost basis proportionally

- Updates cash balance (adds sale proceeds)
- Adjusts portfolio holdings
- Recalculates portfolio_summary

## update_portfolio_and_log.py

Execute trade and atomically update both portfolio.json and trade_log.csv.

### Usage

```bash
python scripts/update_portfolio_and_log.py \
  --ticker TCOM \
  --action BUY \
  --shares 84 \
  --price 61.09 \
  --thesis-status PENDING \
  --reasoning "Strong technical setup, thesis validating"
```

### Parameters

- `--ticker`: Stock ticker symbol (required)
- `--action`: Trade type (options: BUY, SELL, TRIM) (required)
- `--shares`: Number of shares (required)
- `--price`: Price per share (required)
- `--thesis-status`: Thesis validation status (required for BUY)
- `--reasoning`: Investment rationale or trade explanation (required)

### Behavior

**BUY actions**:
- Adds holding to portfolio
- Deducts cost from cash
- Logs trade in trade_log.csv
- Validates thesis-status provided

**SELL actions**:
- Removes entire holding from portfolio
- Adds sale proceeds to cash
- Logs trade in trade_log.csv

**TRIM actions**:
- Removes partial shares from holding
- Adds partial proceeds to cash
- Updates cost basis proportionally
- Logs trade in trade_log.csv

**Atomic updates**: Uses file locking and ensures both portfolio.json and trade_log.csv update together.

## get_trade_log.py

Return trade history with filtering options.

### Usage

```bash
# Get last 10 trades
python scripts/get_trade_log.py --limit 10

# Get trades for specific ticker
python scripts/get_trade_log.py --ticker NVDA

# Get all trades
python scripts/get_trade_log.py
```

### Parameters

- `--limit`: Maximum number of trades to return (optional)
- `--ticker`: Filter by ticker symbol (optional)
- `--format`: Output format (options: json, human) (default: human)

### Output

Array of trade objects with:
- `timestamp`: Trade execution time
- `ticker`: Stock symbol
- `action`: BUY, SELL, or TRIM
- `shares`: Number of shares
- `price`: Price per share
- `cost_basis`: Total cost or proceeds
- `portfolio_pct`: Portfolio percentage after trade
- `thesis_status`: Thesis status at time of trade
- `reasoning`: Trade rationale

## File Structure

### portfolio.json

```json
{
  "holdings": [
    {
      "ticker": "NVDA",
      "shares": 100,
      "cost_basis": 15025.00,
      "current_price": 160.50,
      "market_value": 16050.00,
      "gain_loss": 1025.00,
      "gain_loss_pct": 6.83,
      "portfolio_pct": 15.2,
      "thesis_status": "VALIDATING"  # PENDING, VALIDATING, STRONGER, WARNING, or DANGER
    }
  ],
  "cash": {
    "balance": 50000.00,
    "reserved": 10000.00,
    "available": 40000.00
  },
  "portfolio_summary": {
    "total_value": 105475.00,
    "total_cost": 95425.00,
    "total_gain_loss": 10050.00,
    "total_gain_loss_pct": 10.53,
    "holdings_count": 5,
    "last_updated": "2026-01-16T10:30:00Z"
  },
  "metadata": {
    "version": "1.0",
    "last_updated": "2026-01-16T10:30:00Z"
  }
}
```

### trade_log.csv

CSV with columns:
- `timestamp`: ISO 8601 timestamp
- `ticker`: Stock symbol
- `action`: BUY, SELL, TRIM
- `shares`: Number of shares
- `price`: Price per share
- `cost_basis`: Total cost (negative for buys, positive for sells)
- `portfolio_pct`: Portfolio percentage after trade
- `thesis_status`: Thesis validation status
- `reasoning`: Trade rationale

## Calculations

- **Market Value**: `shares × current_price`
- **Cost Basis**: Weighted average for multiple buys
- **Gain/Loss**: `market_value - cost_basis`
- **Gain/Loss %**: `(gain_loss / cost_basis) × 100`
- **Portfolio %**: `market_value / total_value × 100`

## Thesis Status Tracking

See **Portfolio Management Principles** section in SKILL.md for full classification and sell rules.

Valid thesis_status values:
- **PENDING**: Early stage, validation required
- **VALIDATING**: Catalysts progressing, evidence accumulating
- **STRONGER**: Thesis strengthening with new evidence
- **WARNING**: Thesis at risk, monitor closely
- **DANGER**: Thesis failing or invalidated → SELL

Legacy values (VALIDATED, FAILED, TRANSFORMING, INVALIDATED) are deprecated; map to above values.

## File Locking

All portfolio operations use file locking (`fcntl.flock`) to prevent concurrent modification issues.
