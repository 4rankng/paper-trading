# Portfolio Manager Scripts Reference

Documentation for all portfolio and trade management scripts (v2.1 Multi-Portfolio).

## Architecture

**Shared Cash Pool:** All portfolios share a single cash pool at `portfolios.json` root.
- `cash.amount` is shared across all portfolios
- Position % = `position_value / (holdings_value + shared_cash)`
- `metadata.default_portfolio` specifies the default portfolio

## get_portfolio.py

Return portfolio state with holdings, shared cash, P&L, and summary statistics.

### Usage

```bash
# List all available portfolios
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --list

# Get default portfolio status
python .claude/skills/portfolio_manager/scripts/get_portfolio.py

# Get specific portfolio status
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --portfolio AI_PICKS

# Human-readable format
python .claude/skills/portfolio_manager/scripts/get_portfolio.py --portfolio CORE --format human
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--portfolio` | No | Portfolio name (default: `metadata.default_portfolio`) |
| `--list` | No | List all available portfolios |
| `--format` | No | Output format: json (default) or human |
| `--verbose` | No | Include full holding data (default: concise for LLM) |

### Output

```json
{
  "status": "success",
  "portfolio": "CORE",
  "shared_cash": {"amount": 1000.00, "target_buffer_pct": 15},
  "holdings_count": 5,
  "holdings": [
    {
      "ticker": "NVDA",
      "shares": 100,
      "avg_cost": 150.25,
      "current_price": 160.50,
      "market_value": 16050.00,
      "gain_loss": 1025.00,
      "gain_loss_pct": 6.83,
      "pct_portfolio": 15.2,
      "thesis_status": "VALIDATING"
    }
  ],
  "summary": {
    "holdings_value": 66050.00,
    "total_cost_basis": 55425.00,
    "total_gain_loss": 10625.00,
    "total_gain_loss_pct": 19.17,
    "holdings_count": 5
  },
  "description": "Core long-term holdings"
}
```

---

## get_trade_log.py

Return trade history with filtering options.

### Usage

```bash
# Get last 10 trades
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --limit 10

# Get trades for specific ticker
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --ticker NVDA

# Get trades for specific portfolio
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --portfolio CORE

# Human-readable format
python .claude/skills/portfolio_manager/scripts/get_trade_log.py --limit 5 --format human
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--limit` | No | Maximum number of trades to return |
| `--ticker` | No | Filter by ticker symbol |
| `--portfolio` | No | Filter by portfolio name |
| `--format` | No | Output format: json (default) or human |

---

## update_portfolio_and_log.py

Execute trade and atomically update both `portfolios.json` and `trade_log.csv`.

### Usage

```bash
# Buy in default portfolio
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker TCOM --action BUY --shares 84 --price 61.09 \
  --thesis-status PENDING --reasoning "Strong technical setup"

# Buy in specific portfolio
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker TCOM --action BUY --shares 84 --price 61.09 --portfolio CORE \
  --thesis-status PENDING --reasoning "Strong technical setup"

# Sell entire position
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker LAES --action SELL --shares 5000 --price 4.50 --portfolio CORE \
  --thesis-status VALIDATING --reasoning "Trimming position"

# Trim partial position
python .claude/skills/portfolio_manager/scripts/update_portfolio_and_log.py \
  --ticker PONY --action TRIM --shares 92 --price 16.56 --portfolio CORE \
  --thesis-status VALIDATING --reasoning "Reduce concentration"
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--ticker` | Yes | Stock ticker symbol |
| `--action` | Yes | BUY, SELL, or TRIM |
| `--shares` | Yes | Number of shares (integer) |
| `--price` | Yes | Execution price per share |
| `--thesis-status` | Yes | PENDING, VALIDATING, STRONGER, WARNING, DANGER, FAILED, INVALIDATED |
| `--reasoning` | Yes | Trade rationale |
| `--portfolio` | No | Portfolio name (default: `metadata.default_portfolio`) |
| `--evidence` | No | Evidence file paths |
| `--timestamp` | No | ISO 8601 timestamp (default: now) |

### Behavior

**BUY actions:**
- Adds holding to portfolio (or updates existing)
- Deducts cost from **shared cash pool**
- Logs trade in `trade_log.csv`

**SELL actions:**
- Removes entire holding from portfolio
- Adds sale proceeds to **shared cash pool**
- Logs trade in `trade_log.csv`

**TRIM actions:**
- Removes partial shares from holding
- Adds partial proceeds to **shared cash pool**
- Updates cost basis proportionally
- Logs trade in `trade_log.csv`

---

## File Structure

### portfolios.json

```json
{
  "cash": {
    "amount": 1000.00,
    "target_buffer_pct": 15
  },
  "portfolios": {
    "CORE": {
      "name": "Core Holdings",
      "description": "Long-term compounders",
      "config": {
        "risk_tolerance": "MEDIUM",
        "max_position_pct": 25
      },
      "holdings": [
        {
          "ticker": "NVDA",
          "shares": 100,
          "avg_cost": 150.25,
          "current_price": 160.50,
          "market_value": 16050.00,
          "gain_loss": 1025.00,
          "gain_loss_pct": 6.83,
          "pct_portfolio": 15.2,
          "status": "active",
          "thesis_status": "VALIDATING",
          "thesis_validation_confidence": "HIGH (75%)"
        }
      ],
      "summary": {
        "holdings_value": 66050.00,
        "total_cost_basis": 55425.00,
        "total_gain_loss": 10625.00,
        "total_gain_loss_pct": 19.17,
        "holdings_count": 5
      }
    },
    "AI_PICKS": {
      "name": "AI Picks",
      "description": "High-conviction AI trades",
      "config": {
        "risk_tolerance": "HIGH",
        "max_position_pct": 30
      },
      "holdings": [],
      "summary": {
        "holdings_value": 0.00,
        "total_cost_basis": 0.00,
        "total_gain_loss": 0.00,
        "total_gain_loss_pct": 0.00,
        "holdings_count": 0
      }
    }
  },
  "metadata": {
    "base_currency": "USD",
    "default_portfolio": "CORE",
    "last_updated": "2026-01-30T00:00:00.000000Z",
    "version": "2.1",
    "notes": "Shared cash pool across all portfolios - portfolios only contain stock positions"
  }
}
```

### trade_log.csv

Columns:
- `timestamp`: ISO 8601 timestamp
- `portfolio`: Portfolio name (CORE, AI_PICKS, etc.)
- `ticker`: Stock symbol
- `action`: BUY, SELL, or TRIM
- `shares`: Number of shares
- `price`: Price per share
- `cost_basis`: Cost basis per share
- `portfolio_pct`: Portfolio percentage after trade
- `thesis_status`: Thesis validation status
- `reasoning`: Trade rationale
- `evidence_files`: Comma-separated file paths

---

## Calculations

- **Market Value**: `shares × current_price`
- **Cost Basis**: Weighted average for multiple buys
- **Gain/Loss**: `market_value - (shares × avg_cost)`
- **Gain/Loss %**: `(gain_loss / (shares × avg_cost)) × 100`
- **Portfolio %**: `market_value / (holdings_value + shared_cash) × 100`

---

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Portfolio 'X' not found` | Invalid portfolio name | Use `--list` to see available portfolios |
| `Portfolios not found` | `portfolios.json` missing | Create `portfolios.json` with proper structure |
| `Invalid ticker format` | Ticker not 1-5 letters | Use valid ticker symbol |
| `Position not found` | Cannot sell non-existent holding | Check holdings with `get_portfolio.py` |
| `Insufficient shares` | Selling more than owned | Check share count in holding |
